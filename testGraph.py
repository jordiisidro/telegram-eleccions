import matplotlib.pyplot as plt
def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.2f}%  ({v:d})'.format(p=pct,v=val)
    return my_autopct


# Pie chart, where the slices will be ordered and plotted counter-clockwise:
labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'
sizes = [105, 30, 45, 10]
colors = ['red','green','blue', 'purple']

fig1, ax1 = plt.subplots()
ax1.pie(sizes, labels=labels,  autopct=make_autopct(sizes),
        startangle=90, colors=colors)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.title('String Title Here')
#plt.xlabel('X Axis Title Here')
#plt.ylabel('Y Axis Title Here')
#plt.show()
fig1.savefig('images/pie.png')   # save the figure to file
plt.close(fig1)  


val = [51,22,13,34,75,51,22,13,34,75,51,22,13,34,75]    # the bar lengths
pos = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]    # the bar centers on the y axis
label=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o']


fig2, ax2 = plt.subplots()
ax2.barh(pos,val,ecolor='r', align='center', label=label)
plt.yticks(pos, ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o'])
plt.title('How fast do you want to go today?')
for i, v in enumerate(val):
    ax2.text( v-7, i+.95 , str(v), color='black', fontweight='bold')

#fig2.savefig('images/bar.png')   # save the figure to file
show()
#plt.close(fig2)  
