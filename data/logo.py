import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

red='#730000'
yellow='#E1C800'

fig,ax=plt.subplots(figsize=(1,1),subplot_kw={'projection':'polar'})
verticies=np.array([0,72,144,216,284,360])+90
plt.plot(np.linspace(0,2*np.pi,1000),np.ones(1000),color='none') #force a square plot
plt.fill_between(verticies*np.pi/180,np.ones_like(verticies),np.zeros_like(verticies),color=yellow,lw=0)
plt.fill_between(verticies*np.pi/180,np.ones_like(verticies)*0.85,np.zeros_like(verticies),color=red,lw=0)
ax.set_facecolor('none')
ax.set_axis_off()
ax.text(0.5,0.425,'5',va='center',ha='center',color=yellow,fontsize=32,transform=ax.transAxes)
plt.ylim(0,1)
plt.savefig('logo.png',bbox_inches='tight',dpi=333,transparent=True,pad_inches=0)
# plt.show()
logo=Image.open('logo.png')
logo.save('logo.ico',format='ICO',sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(24,24),(16,16)])
