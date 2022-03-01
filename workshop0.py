#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Workshop 1 - main file

Created on Fri Feb 25 13:52:08 2022

@author: olivi
"""

# Revision history
# 2022-02-28 early version, almost functional (dump and run missing)
# 2022-03-01 release candidate

# generic dependencies
import datetime, os, socket, getpass

# import script, forcefield and struct classes
from pizza.script import *
from pizza.forcefield import *
from pizza.private.struct import struct


# %% Initialization template
class initialization(globalsection):
    """ initialize LAMMPS core-shell model"""
    description = "syntax: initialization(var1=val1,var2=val2,...)"
    userid = "initialization"               # user name
    version = 1.0                           # version
    
    # SMD Scheme (these variables are available everywhere)
    DEFINITIONS = scriptdata(
                units= "$ si",
            dimension= 2,
             boundary= "$ p f p", # simulation box boundaries
          comm_modify= "$ vel yes",
           comm_style= "$ tiled",
          atom_modify= "$ map array",
               newton= "$ off",
              neighbor= "$ 1 bin",
    neigh_modify_every= 5, 
    neigh_modify_delay= 0,
    neigh_modify_check= "$ yes",
            atom_style= "$ smd"
            )
    
    # header
    HEADER = f"# Automatic LAMMPS script (version {script.version})\n" + \
             f"# {getpass.getuser()}@{socket.gethostname()}:{os.getcwd()}\n" + \
             f'# {datetime.datetime.now().strftime("%c")}'
    
    # Template
    TEMPLATE = HEADER + "\n\n# " + "\n# ".join(script._contact) + "\n"*3 + """
# SCHEME INITIALIZATION
units       ${units}
dimension	${dimension}
boundary    ${boundary}
comm_modify ${comm_modify}
comm_style  ${comm_style}
atom_modify ${atom_modify}
newton ${newton}
neighbor	${neighbor}
neigh_modify    every ${neigh_modify_every} delay ${neigh_modify_delay} check ${neigh_modify_check}

atom_style	${atom_style}
 """
    

# %% Initialization template
class load(geometrysection):
    """ load geometry """
    description = 'syntax: load(local="$ /my/folder/",file="$ my file")'
    userid = "load()"
    version = 1.0
    
    # file to load
    DEFINITIONS = scriptdata(
            local = "$ ../datafiles",  # remove the trailing /
             file = "$ 2_Top_mod.lmp",
             mode = "$ add append"
            )
    # Template
    TEMPLATE = \
    """read_data ${local}/${file} ${mode}"""
  
class group(geometrysection):
    """ create groups """
    description = 'group(name="$ mygroup",type="$ 1 2 3")'
    userid = "group()"
    version = 1.0
    
    # group definition
    DEFINITIONS = scriptdata(
        name = "$ solid",
        type = "$ 1 2 3"
        )
    #template
    TEMPLATE = """group ${name} ${type}"""

class gravity(initializesection):
    """ apply gravity """
    description = 'gravity(g=9.81,vector="$ 0 1 0")'
    userid = "gravity()"
    version = 1.0
    
    # group definition
    DEFINITIONS = scriptdata(
             g = 9.81,
        vector = "$ 0 1 0"
        )
    #template
    TEMPLATE = """fix gfix all gravity ${g} vector ${vector} """
    
class interactions(initialization,interactionsection):
    """ set forcefield """
    description = 'interactions(top=1,bottom=2,solid=3,fluid=4)'
    userid = "interactions()"
    version = 1.0
    
    # Properties (used in LAMMPS) - they are interpreted by the proper forcefield
    FLUID = scriptdata(
            rho = 950,
            c0 = 10.0,
            q1 = 1.0,
            Cp = 1.0,
            # hertz contacts
            contact_scale = 1.5,
            contact_stiffness = '10*${c0}^2*${rho}'
        )    
    SOLID = scriptdata(
            rho = 1100,
            c0 = 10.0,
            E = '50*${c0}^2*${rho}',
            nu = 0.3, # Poisson ratio for solid objects
            q1 = 1.0,
            q2 = 0.0,
            Hg = 10,
            Cp = 1.0,
            sigma_yield = '0.1*${E}',
            hardening = 0,
            # hertz contacts
            contact_scale = 1.5,
            contact_stiffness = '50*${c0}^2*${rho}'
        )
    WALL = scriptdata(
            rho = 3000,
            c0 = 10.0,
            contact_stiffness = '50*${c0}^2*${rho}',
            contact_scale = 1.5
        )
       
    # Bead id set at construction
    def __init__(self,top=1,bottom=2,solid=3,fluid=4):
        """ set bead id with interactions(top=1,bottom=2,solid=3,fluid=4) """
        super().__init__() # required to initialize interactions
        self.beadid = scriptdata(top=top,bottom=bottom,solid=solid,fluid=fluid)
        self.forcefield = struct(
            fluid = water(beadtype=fluid, userid="fluid", USER=self.FLUID),
            solid = solidfood(beadtype=solid, userid="solid",USER=self.SOLID),
            top = rigidwall(beadtype=top, userid="top", USER=self.WALL),
            bottom = rigidwall(beadtype=bottom, userid="bottom", USER=self.WALL)
                   )
        self.TEMPLATE = "\n# ===== [ BEGIN FORCEFIELD SECTION ] "+"="*80 +\
                   self.forcefield[0].pair_style() + \
                   self.forcefield.fluid.pair_diagcoeff() + \
                   self.forcefield.solid.pair_diagcoeff() + \
                   self.forcefield.top.pair_diagcoeff() + \
                   self.forcefield.bottom.pair_diagcoeff() + \
                   self.forcefield.bottom.pair_offdiagcoeff(self.forcefield.top) + \
                   self.forcefield.bottom.pair_offdiagcoeff(self.forcefield.fluid) + \
                   self.forcefield.bottom.pair_offdiagcoeff(self.forcefield.solid) + \
                   self.forcefield.top.pair_offdiagcoeff(self.forcefield.fluid) + \
                   self.forcefield.top.pair_offdiagcoeff(self.forcefield.solid) + \
                   self.forcefield.solid.pair_offdiagcoeff(self.forcefield.fluid) + \
                   "\n# ===== [ END FORCEFIELD SECTION ] "+"="*82+"\n"
        self.DEFINTIONS = scriptdata() # no definitions
        
    # Refresh data
    def refresh(self):
        """ refresh values """
        self.__init__(top=self.beadid.top,
                    bottom=self.beadid.bottom,
                    solid=self.beadid.solid,
                    fluid=self.beadid.fluid)
        


# %% Equilibration and dynamics
class thermo(integrationsection):
    DEFINITIONS = scriptdata(
              dt = 0.1,
   adjust_redius = "$ 1.01 10 15",
  limit_velocity = 1000,
         thermo = 50,
  thermo_modify = "$ lost ignore",
        balance = "$ 500 0.9 rcb" # load balancing for MPI
        )
    
    TEMPLATE = """
#   Time integration conditions
fix             dtfix fluid smd/adjust_dt ${dt} # dynamically adjust time increment every step
fix             integration_fix fluid smd/integrate_ulsph adjust_radius ${limit_velocity}
fix             integration_fix_solid solid smd/integrate_tlsph limit_velocity ${limit_velocity}
fix             integration_fix_moving1 moving1 smd/integrate_tlsph limit_velocity ${limit_velocity}
fix             integration_fix_moving2 moving2 smd/integrate_tlsph limit_velocity ${limit_velocity}
#   thermo
thermo		   ${thermo}
thermo_modify  ${thermo_modify}
#   balancing
fix             balance_fix all balance ${balance}
"""

class equilibration(integrationsection):
    """ equilibration(mode="init",limit_velocity=1000,run=1000)  """
    DEFINITIONS = scriptdata(
        velocity = " $0 0 0",
        limit_velocity = 0.01,
        run = [1000,1000]
        )
    
    def __init__(self,mode="init",**args):
        if mode=="init":
            self.TEMPLATE = f"#   Equilibration {mode}" + """
fix             movement1 moving1 smd/setvel ${velocity}
fix             movement2 moving2 smd/setvel ${velocity}
run		${run[0]}
fix             integration_fix_solid solid smd/integrate_tlsph limit_velocity ${limit_velocity}
fix             integration_fix_moving1 moving1 smd/integrate_tlsph limit_velocity ${limit_velocity}
fix             integration_fix_moving2 moving2 smd/integrate_tlsph limit_velocity ${limit_velocity}
run		${run[1]}
"""
        else:
            self.TEMPLATE = f"#   Equilibration {mode}" + """
fix             integration_fix_solid solid smd/integrate_tlsph limit_velocity ${limit_velocity}
fix             integration_fix_moving1 moving1 smd/integrate_tlsph limit_velocity ${limit_velocity}
fix             integration_fix_moving2 moving2 smd/integrate_tlsph limit_velocity ${limit_velocity}
run		${run[0]}
"""
        self.USER = scriptdata(**args)
        if 'run' in self.USER and not isinstance(self.USER.run,list):
            self.USER.run = [self.USER.run]
        
        


# %% DUMP SECTION
class smddump(dumpsection):
    """ dump section """
    DEFINITIONS = scriptdata(
        outstep = 7000,
     outputfile = "$ dump.file"
        )

    TEMPLATE = """
#   Computes
compute         eint all smd/internal/energy
compute         contact_radius all smd/contact/radius
compute         S solid smd/tlsph/stress
compute         nn fluid smd/ulsph/num/neighs
compute         epl solid smd/plastic/strain
compute         vol all smd/vol
compute         rho all smd/rho

#   Dump file
dump            dump_id all custom ${outstep} ${outputfile} id type x y z &
                fx fy fz vx vy vz c_eint c_contact_radius mol &
                c_S[1] c_S[2] c_S[3] c_S[4] mass c_epl c_vol c_rho c_nn proc
dump_modify     dump_id first yes
"""

# %% DISPLACEMENTS and integration
class translation(runsection):
    """ translation """
    DEFINITIONS = scriptdata(
        velocity1 = [0,-1,0],
        velocity2 = [0,1,0],
        force = [0,0,0],
        run = 5000
        )
    TEMPLATE = """
#   Translation
fix             movement1 moving1 smd/setvel ${velocity1[0]} ${velocity1[1]} ${velocity1[2]}
fix             movement2 moving2 smd/setvel ${velocity2[0]} ${velocity2[1]} ${velocity2[2]}
fix             force1 moving1 setforce ${force[0]} ${force[1]} ${force[2]}
run		${run}
"""

class rampforce(runsection):
    """ force ramp """
    DEFINITIONS = scriptdata(
        ramp = (-1,10),
        run = 5000
        )
    TEMPLATE = """
#   Force ramp
variable        ramp equal ramp(${ramp[0]},${ramp[1]})
fix             movement1 moving1 smd/setvel 0 NULL 0
fix             movement2 moving2 smd/setvel 0 0 0
fix             force1 moving1 setforce 0 v_ramp 0
run		${run}
"""


# %% DEBUG  
# ===================================================   
# main()
# ===================================================   
# for debugging purposes (code called as a script)
# the code is called from here
# ===================================================
if __name__ == '__main__':
    
    # initizalization of the scheme (note that c0 is note used in DEFINITIONS)
    init = initialization(c0=12) # 12 to see how to change sound velocity
    init.c0 = 13                 # works also
    init.do()                    # shows the script
    
    # read input data
    # help with load.description
    wdir = "$ ../datafile"
    geom = load(local=wdir,file="$ 2_Top_mod.lmp",mode="") & \
           load(local=wdir,file="$ 1_Bottom_mod.lmp") & \
           load(local=wdir,file="$ 3_thin_shell_outer_mod.lmp") & \
           load(local=wdir,file="$ 4_thin_shell_inner_mod.lmp")
    # create groups
    # help with groups.description
    groups = group(name="$ solid",type="$ 1 2 3") & \
             group(name="$ tlsph",type="$ 1 2 3") & \
             group(name="$ fluid",type="$ 4") & \
             group(name="$ ulsph",type="$ 4") & \
             group(name="$ moving1",type="$ 1") & \
             group(name="$ moving2",type="$ 2")
    # add gravity
    # help with physgravity.description
    physgravity = gravity(g=0)
    
    # interactions (do not forget to refresh)
    forcefield = interactions(top=1,bottom=2,solid=3,fluid=4)
    forcefield.FLUID.rho = 951
    forcefield.refresh() # mandatory after a value modification
    
    
    # equilibration
    initthermo = thermo()
    equilsteps = equilibration(mode="init",run=[1000,2000]) & \
                 equilibration(mode="fast",limit_velocity=1000,run=1000) & \
                 equilibration(mode="slow",limit_velocity=0.01,run=1000) & \
                 equilibration(mode="fast",limit_velocity=1000,run=1000)
  
    # dump
    dump = smddump(outstep=5000,outputfile="$ dump.workshop0")
    
    # displacements
    moves = translation(velocity1 = [0,-1,0], velocity2 = [0,1,0],run=5000) & \
            translation(velocity1 = [0,-0.1,0], velocity2 = [0,0.1,0],run=2000) & \
            translation(force=[0,-1,0], velocity1 = [0,0,0], velocity2 = [0,0,0],run=21000) & \
            rampforce(ramp=(-1,-10), velocity1 = [0,0,0], velocity2 = [0,0,0],run=21000)
  
    # full script
    fullscript = init+geom+groups+physgravity+forcefield+\
        initthermo+equilsteps+dump+moves
    fullscript.write("tmp/myscript.inp")