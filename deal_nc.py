"""
# 处理grib转换完成的nc文件
"""

from netCDF4 import Dataset
import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os, time, math
class diag_nc(object):
    def __init__(self, file_in):
        """
        convert specified grib2 file into nc file
        and read the nc file
        :param file_in: the input grib2 file
        """
        self.start = time.clock()
        path_ori = os.getcwd()
        file_nc = file_in.lstrip('fnl_').replace('grib2', 'nc')
        path_grib = r'C:\Python_learn\pycharm\download_FNL\grib_file'
        path_nc = r'C:\Python_learn\pycharm\download_FNL\nc_file'
        path_wgrib2 = r'C:\Python_learn\pycharm\download_FNL\wgrid2'
        if os.path.exists(os.path.join(path_nc, file_nc)): #文件已经存在
            print('{} already exists.'.format(file_nc))
        else:
            print('convert {} to nc format...'.format(file_in))
            os.system('{} {} -netcdf {}'.format(os.path.join(path_wgrib2,'wgrib2'),
                                                os.path.join(path_grib,file_in),
                                                os.path.join(path_nc, file_nc)))
        self.fid = Dataset(os.path.join(path_nc, file_nc),mode = 'r')
    def read_diag_nc(self):
        """
        read nc file, interp to the specified vertical level
        and diagnose use PJ model
        """
        # 用到的变量：
        # PRMSL_meansealevel, TMP_2maboveground, RH_2maboveground, UGRD_10maboveground, VGRD_10maboveground
        # LANDN_surface, TMP_surface, latitude, longitude, time
        self.t2 = np.squeeze(self.fid.variables['TMP_2maboveground']) - 273.2
        self.rh2 = np.squeeze(self.fid.variables['RH_2maboveground'])
        u10 = np.squeeze(self.fid.variables['UGRD_10maboveground'])
        v10 = np.squeeze(self.fid.variables['VGRD_10maboveground'])
        ws10 = np.sqrt(u10**2 + v10 **2) * 0.2
        # self.ws2 = self.interp_wind(ws10)
        self.ts = np.squeeze(self.fid.variables['TMP_surface']) - 273.2
        self.landmask = np.squeeze(self.fid.variables['LANDN_surface']) # land=1,sea=0
        self.lon = np.squeeze(self.fid.variables['longitude'])
        self.lat = np.squeeze(self.fid.variables['latitude'])
        self.time1 = self.fid.variables['time'].reference_date
        self.hevd = np.full(np.shape(ws10), np.nan)
        self.path_pj = r'C:\Python_learn\pycharm\download_FNL\duct_model\Projects\Console1\Console1\Debug\PJ_2m.exe'
        print('diagnosing ...')
        for i in range(90, 113): #(np.shape(hevd)[0]): # latitude
            for j in range(100,125): #(np.shape(hevd)[1]): # longitude
                if self.landmask[i,j] == 0: # sea
                    r = os.popen('{} {:.1f} {:.1f} {:.1f} {:.1f}'.format
                                 (self.path_pj, self.t2[i, j], self.ts[i, j], self.rh2[i, j],
                                  self.interp_wind(ws10[i, j])))
                    # print('{} {:.1f} {:.1f} {:.1f} {:.1f},lon,{:.1f},lat,{:.1f}'.format
                    #              (self.path_pj,self.t2[i,j], self.ts[i,j], self.rh2[i,j], self.ws10[i,j],
                    #              self.lon[j],self.lat[i] ))
                    try:
                        self.hevd[i,j] =  float(r.read())
                        # print(self.hevd[i,j])
                    except:
                        self.hevd[i, j] = np.nan
                else: # land
                    self.hevd[i,j] = np.nan
        print('diagnose complete!')
    def interp_wind(self, ws10):
        """
        vertical interpolate from 10 m to 2 m
        use profile formula: u = aln(z/z0),or, u = a(lnz - b)
        where z0 use PJ-model roughness z0 = 0.00015
        :param ws10: 10 m wind speed
        :return: 2m wind speed
        """
        z0 = 0.00015
        # ws2[i,j] = ( 2.0 - z0 ) * ws10[i,j]/math.log(10.0 - z0)
        ws2 = (2.0 - z0) * ws10 / math.log(10.0 - z0)
        return ws2
# draw_image = True
# if draw_image:
    def draw_hevd(self):
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        f2 = plt.figure(figsize = (5,5),dpi = 100)
        # m = Basemap(projection='cyl',llcrnrlat=self.lat[0], urcrnrlat=self.lat[-1],
        #             llcrnrlon=self.lon[0],urcrnrlon=self.lon[-1],resolution='c')
        m = Basemap(projection='cyl',llcrnrlat=0.0, urcrnrlat=23.0,
                    llcrnrlon=100.0,urcrnrlon=125.0,resolution='c')
        lon1,lat1 = np.meshgrid(self.lon,self.lat)
        xi,yi = m(lon1, lat1)
        cs = m.contourf(xi, yi, self.hevd,linestyles='solid',cmap = cm.jet, levels = np.arange(0,41.0,2.0))#levels = np.arange(-2,33,2)
        cs1 = m.contour(xi, yi, self.hevd, linestyles='solid', linewidths = 0.5,
                        levels=np.arange(0, 41.0, 6.0), colors = 'k')  # levels = np.arange(-2,33,2)
        m.fillcontinents(color=(0.8, 0.8, 0.8), lake_color=(0.8, 0.8, 0.8))
        m.drawparallels(np.arange(-90., 91., 10.), labels=[1,0,0,0], fontsize=10)
        m.drawmeridians(np.arange(-180., 181., 20.), labels=[0,0,0,1], fontsize=10)
        m.drawcoastlines()
        cbar = m.colorbar(cs, location='right')
        plt.clabel(cs1, fontsize=10, colors='k',fmt = '%.0f')
        plt.title('蒸发波导高度 {}'.format(self.time1))
        self.end1 = time.clock()
        print('Program totally run for %.1f s' %(self.end1 - self.start))
        plt.savefig('tmp.png',dpi = 600)
        plt.show()
if __name__ == "__main__":
    file_grib = r'fnl_20190429_12_00.grib2'
    hc = diag_nc(file_grib)
    draw_image = True
    hc.read_diag_nc()
    hc.draw_hevd()