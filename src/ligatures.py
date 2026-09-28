"""Programming ligatures built from one-cell contextual alternates.

Each source character remains one shaped glyph, one cluster and one 512-unit
advance. Drawing may join across cell edges, but the cursor grid never changes.
"""
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

SEQUENCES=('!=','!==','==','===','<=','>=','->','<-','=>','<=>','<->',
           '-->','<--','==>','<==','<<','>>','<<<','>>>','::',':=',
           '&&','||','++','--','..','...','??','?.')
OPERATOR_CHARS='!<>=-+:&|.?*/%^~'


def artwork(sequence,bold=False):
    """An upright operator drawing in a 16px-high, N-cell pixel canvas."""
    width=8*len(sequence);ink=set();thick=2 if bold else 1
    def pixel(x,y):
        if 0<=x<width and 0<=y<16:ink.add((x,y))
    def h(x0,x1,y):
        for x in range(x0,x1+1):
            for dy in range(thick):pixel(x,y+dy)
    def v(x,y0,y1):
        for y in range(y0,y1+1):
            for dx in range(thick):pixel(x+dx,y)
    def diag(x0,y0,x1,y1):
        steps=max(abs(x1-x0),abs(y1-y0))
        for i in range(steps+1):
            x=round(x0+(x1-x0)*i/max(1,steps));y=round(y0+(y1-y0)*i/max(1,steps))
            for dx in range(thick):pixel(x+dx,y)
    def head(x,direction):
        diag(x-direction*4,3,x,7);diag(x,7,x-direction*4,11)
    def chevron(x,direction):head(x,direction)
    if sequence in ('->','<-','=>','<=>','<->','-->','<--','==>','<=='):
        left=sequence.startswith('<');right=sequence.endswith('>');double='=' in sequence
        x0=1 if left else 2;x1=width-3 if right else width-3
        if double:
            h(x0+2 if left else x0,x1-2 if right else x1,5)
            h(x0+2 if left else x0,x1-2 if right else x1,9)
        else:h(x0,x1,7)
        if left:head(1,-1)
        if right:head(width-3,1)
    elif sequence in ('==','===','!=','!=='):
        ys=(4,7,10) if len(sequence)==3 else (5,9)
        for y in ys:h(2,width-3,y)
        if sequence.startswith('!'):diag(width//2+3,2,width//2-3,12)
    elif sequence in ('<=','>='):
        if sequence=='<=':
            diag(width-4,3,3,7);diag(3,7,width-4,10)
        else:
            diag(3,3,width-4,7);diag(width-4,7,3,10)
        h(3,width-4,13)
    elif set(sequence) in ({'<'},{'>'}):
        for i in range(len(sequence)):
            chevron(2+8*i if sequence[0]=='<' else 5+8*i,-1 if sequence[0]=='<' else 1)
    elif sequence=='::':
        for x in (5,10):
            for y in (5,9):
                pixel(x,y);pixel(x+1,y);pixel(x,y+1);pixel(x+1,y+1)
    elif sequence==':=':
        for y in (5,9):
            pixel(3,y);pixel(4,y);pixel(3,y+1);pixel(4,y+1);h(7,13,y)
    elif sequence=='++':
        h(2,13,7);v(5,4,10);v(10,4,10)
    elif sequence=='--':h(2,13,7)
    elif sequence in ('..','...'):
        for i in range(len(sequence)):
            for x in (5+6*i,6+6*i) if len(sequence)==3 else (5+4*i,6+4*i):
                for y in (10,11):pixel(x,y)
    elif sequence=='||':v(5,3,11);v(10,3,11)
    elif sequence=='&&':
        # Two recognizable ampersands, brought together with a continuous
        # baseline stroke; never replace logical-and with a different symbol.
        rows=[0x30,0x48,0x48,0x30,0x6a,0xcc,0xcc,0xcc,0x76]
        for i in range(2):
            for y,b in enumerate(rows,3):
                for x in range(7):
                    if b&(128>>x):pixel(i*8+x,y)
        h(5,9,11)
    elif sequence in ('??','?.'):
        for i in range(2 if sequence=='??' else 1):
            x=i*8
            h(x+2,x+4,3);pixel(x+1,4);v(x+5,4,5);diag(x+5,5,x+3,7);v(x+3,7,8)
            pixel(x+3,11);pixel(x+4,11)
        if sequence=='?.':
            for x in (11,12):
                for y in (10,11):pixel(x,y)
    else:raise ValueError(sequence)
    return tuple(frozenset(x for x,y0 in ink if y0==y) for y in range(16))


def add_glyphs(glyf,order,draw,bold):
    mapping={}
    for index,sequence in enumerate(SEQUENCES):
        rows=artwork(sequence,bold)
        names=[]
        for position in range(len(sequence)):
            name=f'lig{index:02d}.part{position}'
            piece=[{x-position*8 for x in row if position*8<=x<(position+1)*8} for row in rows]
            glyf[name]=draw(piece);order.append(name);names.append(name)
        mapping[sequence]=names
    return mapping


def add_features(font,mapping):
    def original(c):return f'uni{ord(c):04X}'
    operators=[original(c) for c in OPERATOR_CHARS]+[g for names in mapping.values() for g in names]
    lines=['languagesystem DFLT dflt;','languagesystem latn dflt;',
           '@operators = ['+' '.join(operators)+'];','feature calt {']
    for index,sequence in sorted(enumerate(SEQUENCES),key=lambda pair:(-len(pair[1]),pair[0])):
        names=mapping[sequence];base=[original(c) for c in sequence]
        lines.append(f'lookup seq{index} {{')
        # Only exact complete operator runs. Avoid transforming the first three
        # characters of ==== or the tail of a different longer operator.
        lines.append('ignore sub @operators '+base[0]+"' "+' '.join(base[1:])+';')
        lines.append('ignore sub '+base[0]+"' "+' '.join(base[1:])+' @operators;')
        lines.append('sub '+base[0]+"' "+' '.join(base[1:])+' by '+names[0]+';')
        for pos in range(1,len(sequence)):
            prefix=' '.join(names[:pos]);suffix=' '.join(base[pos+1:])
            lines.append('sub '+prefix+' '+base[pos]+"' "+suffix+' by '+names[pos]+';')
        lines.append(f'}} seq{index};')
    lines.append('} calt;')
    addOpenTypeFeaturesFromString(font,'\n'.join(lines))
    return '\n'.join(lines)+'\n'
