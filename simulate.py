"""Standalone Tomasulo-style scheduler; legacy Verilog integration is preserved in tomo.py."""
import argparse
import json
import operator
import re
from pathlib import Path

OPS = {'ADD': operator.add, 'SUB': operator.sub, 'FADD': operator.add,
       'MUL': operator.mul, 'FMUL': operator.mul, 'AND': operator.and_,
       'OR': operator.or_, 'XOR': operator.xor, 'NAND': lambda a,b: ~(a&b),
       'NOR': lambda a,b: ~(a|b), 'XNOR': lambda a,b: ~(a^b),
       'LSL': operator.lshift, 'LSR': operator.rshift, 'CMP': lambda a: ~a}
LATENCY = {'ADD':6, 'SUB':6, 'MUL':11, 'FADD':21, 'FMUL':24,
           'LDR':2, 'STR':2, 'LSL':4, 'LSR':4}

def register(token):
    if not re.fullmatch(r'R(?:[0-9]|[12][0-9]|3[01])', token):
        raise ValueError(f'Invalid register: {token}')
    return int(token[1:])

def parse(text):
    program=[]
    for raw in text.splitlines():
        line=raw.split('#',1)[0].strip()
        if not line: continue
        fields=line.replace(',', ' ').split(); op=fields[0].upper()
        if op not in OPS and op not in {'LDR','STR'}: raise ValueError(f'Unsupported operation: {op}')
        expected=3 if op in {'LDR','STR','CMP'} else 4
        if len(fields)!=expected: raise ValueError(f'Invalid instruction: {line}')
        register(fields[1])
        if op in {'LDR','STR'}:
            match=re.fullmatch(r'(-?\d+)\+(R\d+)|(R\d+)\+(-?\d+)|(R\d+)', fields[2])
            if not match: raise ValueError(f'Invalid address: {fields[2]}')
            if match[1] is not None: offset,base=int(match[1]),match[2]
            elif match[3] is not None: offset,base=int(match[4]),match[3]
            else: offset,base=0,match[5]
            register(base); args=[base]; dest=fields[1] if op=='LDR' else None
            if op=='STR': args.append(fields[1])
        else:
            args=fields[2:];offset=0;dest=fields[1]
            for arg in args:
                if arg.startswith('R'):register(arg)
                else:float(arg) # validate immediates without eval
        group='mem' if op in {'LDR','STR'} else 'mul' if op in {'MUL','FMUL'} else 'add' if op in {'ADD','SUB','FADD'} else 'logic'
        program.append(dict(text=line,op=op,args=args,dest=dest,offset=offset,group=group))
    return program

def simulate(text, registers=None, memory=None, max_cycles=10000, latencies=None):
    program=parse(text); regs=list(range(32)) if registers is None else list(registers)
    if len(regs)!=32:raise ValueError('Exactly 32 register values are required')
    mem={} if memory is None else dict(memory); tags=[None]*32; stations=[]; trace=[]
    statuses=[dict(instruction=p['text'],issue=None,start=None,finish=None,write=None) for p in program]
    capacity={'add':3,'mul':2,'logic':2,'mem':3}; delays={**LATENCY,**(latencies or {})}; front=0
    for cycle in range(1,max_cycles+1):
        # One CDB result per cycle. Completed instructions keep their station until broadcast.
        ready=[s for s in stations if s['finish'] is not None and s['finish']<cycle]
        if ready:
            s=min(ready,key=lambda s:(s['finish'],s['id'])); tag=s['id'];value=s['result']
            if s['op']=='STR':mem[s['address']]=value
            else:
                for other in stations:
                    for operand in other['operands']:
                        if operand[1]==tag:operand[:]=[value,None]
                dest=register(s['dest'])
                if tags[dest]==tag:regs[dest]=value;tags[dest]=None
            statuses[tag]['write']=cycle; stations.remove(s)
        busy={s['group'] for s in stations if s['start'] is not None and s['finish'] is None}
        for s in stations:
            if s['start'] is not None or s['group'] in busy or any(o[1] is not None for o in s['operands']):continue
            if s['group']=='mem' and any(o['group']=='mem' and o['id']<s['id'] for o in stations):continue
            s['start']=cycle;statuses[s['id']]['start']=cycle;busy.add(s['group'])
        for s in stations:
            if s['start'] is None or s['finish'] is not None or cycle<s['start']+delays.get(s['op'],1)-1:continue
            values=[o[0] for o in s['operands']]
            if s['op'] in {'LDR','STR'}:
                s['address']=int(values[0])+s['offset'];s['result']=mem.get(s['address'],0) if s['op']=='LDR' else values[1]
            else:
                if s['op'] not in {'ADD','SUB','MUL','FADD','FMUL'}:values=list(map(int,values))
                s['result']=OPS[s['op']](*values)
            s['finish']=cycle;statuses[s['id']]['finish']=cycle
        if front<len(program):
            p=program[front]
            if sum(s['group']==p['group'] for s in stations)<capacity[p['group']]:
                operands=[]
                for a in p['args']:
                    if a.startswith('R'):
                        r=register(a);operands.append([regs[r] if tags[r] is None else None,tags[r]])
                    else:operands.append([float(a),None])
                s={**p,'id':front,'operands':operands,'start':None,'finish':None,'result':None};stations.append(s)
                if p['dest'] is not None:tags[register(p['dest'])]=front
                statuses[front]['issue']=cycle;front+=1
        trace.append(dict(cycle=cycle,registers=regs.copy(),register_tags=tags.copy(),stations=[dict(id=s['id'],op=s['op'],group=s['group'],operands=[o.copy() for o in s['operands']],start=s['start'],finish=s['finish']) for s in stations]))
        if front==len(program) and not stations:return dict(registers=regs,memory=mem,cycles=cycle,instructions=statuses,trace=trace)
    raise RuntimeError(f'Cycle limit {max_cycles} reached')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('program',type=Path);parser.add_argument('--output',type=Path);parser.add_argument('--max-cycles',type=int,default=10000)
    args=parser.parse_args()
    try:result=simulate(args.program.read_text(),max_cycles=args.max_cycles)
    except (ValueError,RuntimeError) as e:parser.error(str(e))
    content=json.dumps(result,indent=2)
    if args.output:args.output.write_text(content+'\n')
    else:print(content)
