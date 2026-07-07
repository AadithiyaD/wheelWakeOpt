def _normalize(self, x): 
    """ normalize input x by min max of stored x (not of argument x) """
    denom = self.x_max - self.x_min
    denom[denom==0.0] = 1.0 # avoid divide by zero
    x_norm = (x - self.x_min)/denom
    return x_norm
 
    
def add_interpolator(self, interpolator='nearest' ):
    """ create private interpolator """
    if not self.constants:
        # normalize inputs, important for RBF
        x_norm = self._normalize(self.x)
        if interpolator == 'RBF':                
            self._interp = RBFInterpolator(x_norm,self.y)
        elif interpolator == 'linear':
            self._interp = LinearNDInterpolator(x_norm,self.y)
        else:
            # default is guaranteed to work
            self._interp = NearestNDInterpolator(x_norm,self.y)
        return
    else:
        return # really need to throw an exception

def interpolate(self,x):
    """ interpolate the outputs y based on array of inputs """
    # interpolator works on normalised inputs
    x_norm = self._normalize(x)
    y = self._interp(x_norm) 
    return y    
    
def plot_2d(self, x1name, x2name, yname, interpolate=False, resolution=50, **kwargs):
    """ contour plotting with 2 inputs and 1 output, use input values to downselect
    default is to triangulate points, if interpolation available will use
    that function with resolution points """
    # extract columns
    x1_i = self.get_x(x1name);  x2_i = self.get_x(x2name)
    y_i = self.get_y(yname)
    
    # find indices
    x1_index = self.get_x_index(x1name);  x2_index = self.get_x_index(x2name); 
    y_index = self.get_y_index(yname)
    
    # use indices to extract units
    x1_name = self.x_names[x1_index];  x2_name = self.x_names[x2_index];    
    y_name = self.y_names[y_index]
    x1_unit = self.x_units[x1_index];  x2_unit = self.x_units[x2_index];    
    y_unit = self.y_units[y_index]
    
    if interpolate:
        # set default inputs for interpolation as the means
        x = self.x_mean.copy() # avoid having a view that over-writes x_mean
        x = np.reshape(x, (1,-1))
    
        # go through keyword arguments
        for keyword, value in kwargs.items():
            # find column index of input for keyword argument
            xcol = self.x_names.index(keyword)
            # ensure inputs are within allowable range of data
            minval = self.x_min[xcol]; maxval = self.x_max[xcol]
            x[0,xcol] = np.clip(value, minval, maxval)
                        
        # replicate this row resolution times
        x = np.repeat(x, resolution*resolution, axis=0)
    
        # create resolution points in the range of x1 and x2
        x_min = self.x_min[x1_index]; x_max = self.x_max[x1_index];    
        print(f"x1 range: {x_min} to {x_max}")
        x1_i = np.linspace(x_min, x_max, resolution)

        x_min = self.x_min[x2_index]; x_max = self.x_max[x2_index];       
        print(f"x2 range: {x_min} to {x_max}")
        x2_i = np.linspace(x_min, x_max, resolution)
        
        x1g, x2g = np.meshgrid(x1_i,x2_i)
        
        # replace the columns with this new range of x        
        x[:,x1_index] = x1g.flatten()       
        x[:,x2_index] = x2g.flatten()       

        # use interpolator set up previously
        y = self.interpolate(x)
        
        # y contains all outputs,  need to extract required column          
        y_i = y[:,y_index]
        
        yg = y_i.reshape(resolution,resolution)

    if interpolate:
        # use matplotlib separate figures
        fig, ax = plt.subplots()
        ax.set_xlabel(x1_name+' ['+x1_unit+']'); 
        ax.set_ylabel(x2_name+' ['+x2_unit+']')
        ax.contour(x1g, x2g, yg, colors='k')
        cont = ax.contourf(x1g, x2g, yg, cmap="viridis")
        fig.colorbar(cont)
        ax.set_title(y_name+' ['+y_unit+']')      
        plt.savefig("plt.png")      
        plt.show()
        
        
    # else:
    #     # mask to keep rows corresponding to keyword arguments
    #     mask = self._set_mask(**kwargs)
    #     # default mode store for points, may be empty!
    #     x1_i_points = x1_i[mask];   x2_i_points = x2_i[mask];   
    #     y_i_points = y_i[mask]
                
    #     # use matplotlib separate figures
    #     fig, ax = plt.subplots()
    #     ax.set_xlabel(x1_name+' ['+x1_unit+']'); 
    #     ax.set_ylabel(x2_name+' ['+x2_unit+']')
    #     ax.plot(x1_i_points, x2_i_points, 'x', markersize=8, color='k')
    #     tcf= ax.tricontourf(x1_i_points, x2_i_points, y_i_points)
    #     fig.colorbar(tcf)
    #     ax.tricontour(x1_i_points, x2_i_points, y_i_points, colors='k')
    #     ax.set_title(y_name+' ['+y_unit+']')
    #     plt.show()
    #     plt.savefig("plt.png")
        

    return
