import csv
import numpy as np
from scipy.optimize import curve_fit

from astropy.io import fits
import matplotlib.pyplot as plt
import time

t1 = time.time()

def objective(t,b):

    return b*(np.exp(-t)-1)

#time1 = np.arange(0,27,1)

a_values_channel_level = []
b_values_channel_level = []
count_values_channel_level = []

er_a_channel_level = []
er_b_channel_level = []



for channel in range(0,4,1):
    plt.figure()
    #a_values_image_level = []
    b_values_image_level = []
    count_values_image_level = []
    #avs = []
    bvs = []

    #er_a = []
    er_b = []
    counts = []
    cro = 0
    dc = np.load('/home/varghese/Desktop/DS5_DP1/Dataset/Avg_0G/AvgDataCube_0G_{}.npy'.format(channel))
    Sigma2 = np.load('/home/varghese/Desktop/DP1/Codes_Dataset_3/9_readout_error/Long_exp_Variance_channel_{}.npy'.format(channel))
    Sigma1 = np.median(np.sqrt(Sigma2.flatten())) + np.zeros(20)
   # print(Sigma)
    #rows = []
    #fields = ['cro','avg_count','a','b','fit']
    fiber_mask = np.load('/home/varghese/Desktop/DP1/Masks/Needed_fiber_mask.npy')[:,512*channel:(512*(channel+1))]
    interval = 100
    for flux_bin in range(500,60000,interval):
        #rows = []
        
        cro+=1
        pix_mask = (dc[-1] > (flux_bin-interval/2)) & (dc[-1] < (flux_bin+interval/2)) & (fiber_mask ==1)
        avg_count = np.nanmedian(dc[10,pix_mask])
        delta_change_cube = np.nanmedian((dc[10:,pix_mask]-dc[10,pix_mask])*100/dc[10,pix_mask],axis=1)
        time1 = np.arange(0,np.size(delta_change_cube,axis=0),1)
        if not np.isnan(avg_count) and delta_change_cube[-1]<0:
            Sigma = Sigma1*100/(avg_count*np.sqrt(np.sum(pix_mask)))
            #Sigma = Sigma*delta_change_cube/(np.nanmedian(dc[3:,pix_mask]-dc[3,pix_mask])*np.sqrt(np.sum(pix_mask)))
            #print(Sigma,channel,np.sum(pix_mask))
            sub_rows = []
            try:
                if len(bvs)==0:
                    b_ini = 0.5
                else:
                    b_ini = 0.5
                
                fitting_data_variables, error = curve_fit(objective,time1,delta_change_cube,np.array([0.5]),sigma=Sigma)
                b = fitting_data_variables[0]
                
                db = np.sqrt(error[0][0])
                #db = np.sqrt(error[1][1])
                print(b,db)
                plt.figure(figsize=(16,9))
                plt.plot(delta_change_cube,'o-',color='blue')
                plt.plot(objective(time1,b),'--',color='green')
                plt.title('{0},C={1},b={2}, fit'.format(cro,avg_count,b))
                plt.xlabel('time')
                plt.ylabel('Count evolution')
                plt.savefig('Ch_{0}/Fit_{1}.png'.format(channel,cro))
                #avs.append(a)
                bvs.append(b)
                #er_a.append(da)
                er_b.append(db)
                counts.append(avg_count)
            except Exception as e:
                print(e)
                #if avg_count != nan:
                
                print('{0},{1}'.format(avg_count, channel,'cannot be done'))
    
    t2 = time.time()
    print("channel",channel,"done with initials",(t2-t1)//60,'min',int(t2-t1)%60,'s')
    b_values_channel_level.append(bvs)
    count_values_channel_level.append(counts)
    #er_a_channel_level.append(er_a)
    er_b_channel_level.append(er_b)
    #plt.legend()
    #plt.title('Wrong fittings')
    #plt.savefig('wrong_curves_ch{}.png'.format(channel))
    #print(rows)
    
print('parametrization done')
#fig, axs = plt.subplots(4,figsize=(16,9))
plt.title('checking each exposure:a')
color_list = ['black','blue','green','red','dimgray','deepskyblue','lightgreen','lightcoral']

#print(a_values_channel_level)

plt.figure(figsize=(12,6))
for chan in range(4):
     plt.errorbar(count_values_channel_level[chan],b_values_channel_level[chan],yerr=er_b_channel_level[chan],fmt='.',color=color_list[chan],ecolor=color_list[4+chan],elinewidth=1,capsize=10,label='Channel {}'.format(chan+1))#,'.',color=color_list[chan],alpha=0.7,label='{}'.format(chan))
plt.title("a vs count: Dataset 4(19/6/22), $a(e^{-t}-1)$",fontdict={'fontsize': 18})
plt.xlabel('Count(ADU)',fontsize=18)
plt.legend()
#plt.ylim(0.0,0.65)
plt.ylabel('a',fontsize=18)
plt.savefig("DS5_Expo_check_a_exp_l.png")

