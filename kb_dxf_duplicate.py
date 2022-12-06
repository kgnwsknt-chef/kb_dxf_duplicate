#
# kb_dxf_duplicate.py
#                       2022 kgnwsknt-chef
import sys
import os
import json
import re
import ezdxf
#________________________________________
def main():
    if len(sys.argv)<3:
        print('usage: python kb_dxf_duplicate.py KLE.json input.dxf')
        return
    kle_fname = sys.argv[1]
    indxf_fname = sys.argv[2]

    out_fname = sys.argv[1]
    out_fname = out_fname.replace('.json','_json.dxf')

    kle_json = load_kle_json(kle_fname)
    if kle_json==False:
        return

    msp_in = get_msp_from_dxffile(indxf_fname)
    if msp_in==False:
        return
    
    #prepare output dxf
    doc = ezdxf.new('R2010')
    doc.units = ezdxf.units.MM
    msp_out = doc.modelspace()

    generate_dxf(kle_json,msp_in, msp_out)

    doc.saveas(out_fname)
    print('output file = ',out_fname)

#________________________________________
def load_kle_json(fname):
    if not os.path.exists(fname):
        print('file not found:',fname)
        return False
    f = open(fname,"r",encoding="utf-8")
    kle_json = json.load(f)
    return kle_json
#________________________________________
def get_msp_from_dxffile(fname):
    if not os.path.exists(fname):
        print('file not found:',fname)
        return False
    doc = ezdxf.readfile(fname)
    msp = doc.modelspace()
    return msp
#________________________________________
def generate_dxf(kle_json,msp_in, msp_out):
    PITCH=19.05

    irow=0
    cen_x=0
    cen_y=0.5*PITCH
    for row_dict in kle_json:
        width=1
        #    print('--- row = ',irow,'----\n')
        for item in row_dict:

            #print(irow,item,type(item),'')

            # skip header
            if irow==0:
                continue

            # update x position
            if isinstance(item,dict):
                if 'x' in item:
                    dx=item['x']
                    cen_x = cen_x + dx*PITCH
    
            # update y position
            if isinstance(item,dict):
                if 'y' in item:
                    dy=item['y']
                    cen_y = cen_y-dy*PITCH

            # update width
            if isinstance(item,dict):
                if 'w' in item:
                    width=item['w']

    
            # ----- key -----
            if isinstance(item,str):
                item=re.sub('\n.*','',item).lower()
                if not item:
                    item='space'

                cen_x = cen_x + width*0.5*PITCH
                #print(irow,item,cen_x,cen_y,width,'')
                draw_object(cen_x,cen_y,msp_in,msp_out)
                #draw_keybox(cen_x,cen_y,width,msp_out)

                cen_x = cen_x + width*0.5*PITCH
                    
                width=1
            # ----- end of key -----

        irow=irow+1
        cen_x=0
        cen_y=cen_y-PITCH
        # end of row

    # end: for row_dict in kle_json:

    return 

#________________________________________
def draw_object(x,y, msp_in, msp_out):
    offset = (x,y)
    for e in msp_in:
        if e.dxftype()=="LINE":
            sta = e.dxf.start + offset
            sto = e.dxf.end   + offset
            msp_out.add_line(sta,sto)
        if e.dxftype()=="CIRCLE":
            pos = e.dxf.center + offset
            r = e.dxf.radius
            msp_out.add_circle(pos,r)
        if e.dxftype()=="ARC":
            pos = e.dxf.center + offset
            r = e.dxf.radius
            sta = e.dxf.start_angle
            end = e.dxf.end_angle
            msp_out.add_arc(pos,r,sta,end)
        if e.dxftype()=="LWPOLYLINE":
            points = e.get_points()
            flag = e.dxf.flags
            points_aft = []
            for i, row in enumerate(points):
                points_aft.append(tuple([row[0]+x,row[1]+y,row[2],row[3],row[4]]))
            lwp = msp_out.add_lwpolyline(points_aft,"xyseb",close=flag)
#________________________________________
def draw_keybox(x,y,u,msp):
    PITCH=19.05
    msp.add_line((x-0.5*PITCH*u,y-0.5*PITCH),
                 (x+0.5*PITCH*u,y-0.5*PITCH))
    msp.add_line((x+0.5*PITCH*u,y-0.5*PITCH),
                 (x+0.5*PITCH*u,y+0.5*PITCH))
    msp.add_line((x+0.5*PITCH*u,y+0.5*PITCH),
                 (x-0.5*PITCH*u,y+0.5*PITCH))
    msp.add_line((x-0.5*PITCH*u,y+0.5*PITCH),
                 (x-0.5*PITCH*u,y-0.5*PITCH))
#________________________________________
if __name__=="__main__":
    main()
    
#________________________________________
