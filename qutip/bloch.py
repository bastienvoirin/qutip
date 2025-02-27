__all__ = ['Bloch']

import os

from numpy import (ndarray, array, linspace, pi, outer, cos, sin, ones, size,
                   sqrt, real, mod, append, ceil, arange, sign)

from packaging.version import parse as parse_version

from qutip.qobj import Qobj
from qutip.expect import expect
from qutip.operators import sigmax, sigmay, sigmaz

try:
    import matplotlib
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib.patches import FancyArrowPatch
    from mpl_toolkits.mplot3d import proj3d

    # Define a custom _axes3D function based on the matplotlib version.
    # The auto_add_to_figure keyword is new for matplotlib>=3.4.
    if parse_version(matplotlib.__version__) >= parse_version('3.4'):
        def _axes3D(fig, *args, **kwargs):
            ax = Axes3D(fig, *args, auto_add_to_figure=False, **kwargs)
            return fig.add_axes(ax)
    else:
        def _axes3D(*args, **kwargs):
            return Axes3D(*args, **kwargs)

    class Arrow3D(FancyArrowPatch):
        def __init__(self, xs, ys, zs, *args, **kwargs):
            FancyArrowPatch.__init__(self, (0, 0), (0, 0), *args, **kwargs)

            self._verts3d = xs, ys, zs

        def draw(self, renderer):
            xs3d, ys3d, zs3d = self._verts3d
            xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.M)

            self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
            FancyArrowPatch.draw(self, renderer)
except:
    pass

try:
    from IPython.display import display
except:
    pass


class Bloch:
    r"""
    Class for plotting data on the Bloch sphere.  Valid data can be either
    points, vectors, or Qobj objects.

    Attributes
    ----------
    axes : matplotlib.axes.Axes
        User supplied Matplotlib axes for Bloch sphere animation.
    fig : matplotlib.figure.Figure
        User supplied Matplotlib Figure instance for plotting Bloch sphere.
    font_color : str, default 'black'
        Color of font used for Bloch sphere labels.
    font_size : int, default 20
        Size of font used for Bloch sphere labels.
    frame_alpha : float, default 0.1
        Sets transparency of Bloch sphere frame.
    frame_color : str, default 'gray'
        Color of sphere wireframe.
    frame_width : int, default 1
        Width of wireframe.
    point_color : list, default ["b", "r", "g", "#CC6600"]
        List of colors for Bloch sphere point markers to cycle through, i.e.
        by default, points 0 and 4 will both be blue ('b').
    point_marker : list, default ["o", "s", "d", "^"]
        List of point marker shapes to cycle through.
    point_size : list, default [25, 32, 35, 45]
        List of point marker sizes. Note, not all point markers look the same
        size when plotted!
    sphere_alpha : float, default 0.2
        Transparency of Bloch sphere itself.
    sphere_color : str, default '#FFDDDD'
        Color of Bloch sphere.
    figsize : list, default [7, 7]
        Figure size of Bloch sphere plot.  Best to have both numbers the same;
        otherwise you will have a Bloch sphere that looks like a football.
    vector_color : list, ["g", "#CC6600", "b", "r"]
        List of vector colors to cycle through.
    vector_width : int, default 5
        Width of displayed vectors.
    vector_style : str, default '-\|>'
        Vector arrowhead style (from matplotlib's arrow style).
    vector_mutation : int, default 20
        Width of vectors arrowhead.
    view : list, default [-60, 30]
        Azimuthal and Elevation viewing angles.
    xlabel : list, default ["$x$", ""]
        List of strings corresponding to +x and -x axes labels, respectively.
    xlpos : list, default [1.2, -1.2]
        Positions of +x and -x labels respectively.
    ylabel : list, default ["$y$", ""]
        List of strings corresponding to +y and -y axes labels, respectively.
    ylpos : list, default [1.2, -1.2]
        Positions of +y and -y labels respectively.
    zlabel : list, default ['$\\left\|0\\right>$', '$\\left\|1\\right>$']
        List of strings corresponding to +z and -z axes labels, respectively.
    zlpos : list, default [1.2, -1.2]
        Positions of +z and -z labels respectively.
    """
    def __init__(self, fig=None, axes=None, view=None, figsize=None,
                 background=False):
        # Figure and axes
        self.fig = fig
        self.axes = axes
        # Background axes, default = False
        self.background = background
        # The size of the figure in inches, default = [5,5].
        self.figsize = figsize if figsize else [5, 5]
        # Azimuthal and Elevation viewing angles, default = [-60,30].
        self.view = view if view else [-60, 30]
        # Color of Bloch sphere, default = #FFDDDD
        self.sphere_color = '#FFDDDD'
        # Transparency of Bloch sphere, default = 0.2
        self.sphere_alpha = 0.2
        # Color of wireframe, default = 'gray'
        self.frame_color = 'gray'
        # Width of wireframe, default = 1
        self.frame_width = 1
        # Transparency of wireframe, default = 0.2
        self.frame_alpha = 0.2
        # Labels for x-axis (in LaTeX), default = ['$x$', '']
        self.xlabel = ['$x$', '']
        # Position of x-axis labels, default = [1.2, -1.2]
        self.xlpos = [1.2, -1.2]
        # Labels for y-axis (in LaTeX), default = ['$y$', '']
        self.ylabel = ['$y$', '']
        # Position of y-axis labels, default = [1.2, -1.2]
        self.ylpos = [1.2, -1.2]
        # Labels for z-axis (in LaTeX),
        # default = [r'$\left\|0\right>$', r'$\left|1\right>$']
        self.zlabel = [r'$\left|0\right>$', r'$\left|1\right>$']
        # Position of z-axis labels, default = [1.2, -1.2]
        self.zlpos = [1.2, -1.2]
        # ---font options---
        # Color of fonts, default = 'black'
        self.font_color = 'black'
        # Size of fonts, default = 20
        self.font_size = 20
        # Visible back parts of the xyz equators, default = ['x', 'z']
        self.equators_back = ['x', 'z']
        # Visible front parts of the xyz equators, default = ['x', 'z']
        self.equators_front = ['x', 'z']
        
        # ---arc options---
        # List of colors for Bloch arcs, default = ['k']
        self.arc_color = ['k']
        # Width of Bloch arcs, default = 2
        self.arc_width = 2
        
        # ---projection options---
        # List of colors for projections, default = ['k']
        self.projection_color = ['k']
        # Width of projections, default = 2
        self.projection_width = 2
        # Style of projections, default = '--' (dashed line)
        self.projection_style = '--'
        
        # ---trajectory options---
        # List of colors for trajectories, default = ['k']
        self.trajectory_color = ['k']
        # Width of trajectories, default = 2
        self.trajectory_width = 2
        # Style of trajectories, default = '-' (solid line)
        self.trajectory_style = '-'

        # ---vector options---
        # List of colors for Bloch vectors, default = ['b','g','r','y']
        self.vector_color = ['g', '#CC6600', 'b', 'r']
        # Width of Bloch vectors, default = 5
        self.vector_width = 3
        # Style of Bloch vectors, default = '-\|>' (or 'simple')
        self.vector_style = '-|>'
        # Sets the width of the vectors arrowhead
        self.vector_mutation = 20

        # ---point options---
        # List of colors for Bloch point markers, default = ['b','g','r','y']
        self.point_color = ['b', 'r', 'g', '#CC6600']
        # Size of point markers, default = 25
        self.point_size = [25, 32, 35, 45]
        # Shape of point markers, default = ['o','^','d','s']
        self.point_marker = ['o', 's', 'd', '^']

        # ---data lists---
        # Data for point markers
        self.points = []
        # Data for Bloch vectors
        self.vectors = []
        # Data for annotations
        self.annotations = []
        # Data for arcs
        self.arcs = []
        # Data for projections
        self.projections = []
        # Data for trajectories
        self.trajectories = []
        # Number of times sphere has been saved
        self.savenum = 0
        # Style of points, 'm' for multiple colors, 's' for single color
        self.point_style = []

        # status of rendering
        self._rendered = False
        # status of showing
        if fig is None:
            self._shown = False
        else:
            self._shown = True

    def set_label_convention(self, convention):
        """Set x, y and z labels according to one of conventions.

        Parameters
        ----------
        convention : string
            One of the following:

            - "original"
            - "xyz"
            - "sx sy sz"
            - "01"
            - "polarization jones"
            - "polarization jones letters"
              see also: https://en.wikipedia.org/wiki/Jones_calculus
            - "polarization stokes"
              see also: https://en.wikipedia.org/wiki/Stokes_parameters
        """
        ketex = "$\\left.|%s\\right\\rangle$"
        # \left.| is on purpose, so that every ket has the same size

        if convention == "original":
            self.xlabel = ['$x$', '']
            self.ylabel = ['$y$', '']
            self.zlabel = ['$\\left|0\\right>$', '$\\left|1\\right>$']
        elif convention == "xyz":
            self.xlabel = ['$x$', '']
            self.ylabel = ['$y$', '']
            self.zlabel = ['$z$', '']
        elif convention == "sx sy sz":
            self.xlabel = ['$s_x$', '']
            self.ylabel = ['$s_y$', '']
            self.zlabel = ['$s_z$', '']
        elif convention == "01":
            self.xlabel = ['', '']
            self.ylabel = ['', '']
            self.zlabel = ['$\\left|0\\right>$', '$\\left|1\\right>$']
        elif convention == "polarization jones":
            self.xlabel = [ketex % "\\nearrow\\hspace{-1.46}\\swarrow",
                           ketex % "\\nwarrow\\hspace{-1.46}\\searrow"]
            self.ylabel = [ketex % "\\circlearrowleft", ketex %
                           "\\circlearrowright"]
            self.zlabel = [ketex % "\\leftrightarrow", ketex % "\\updownarrow"]
        elif convention == "polarization jones letters":
            self.xlabel = [ketex % "D", ketex % "A"]
            self.ylabel = [ketex % "L", ketex % "R"]
            self.zlabel = [ketex % "H", ketex % "V"]
        elif convention == "polarization stokes":
            self.ylabel = ["$\\nearrow\\hspace{-1.46}\\swarrow$",
                           "$\\nwarrow\\hspace{-1.46}\\searrow$"]
            self.zlabel = ["$\\circlearrowleft$", "$\\circlearrowright$"]
            self.xlabel = ["$\\leftrightarrow$", "$\\updownarrow$"]
        else:
            raise Exception("No such convention.")

    def __str__(self):
        s = ""
        s += "Bloch data:\n"
        s += "-----------\n"
        s += "Number of points:  " + str(len(self.points)) + "\n"
        s += "Number of vectors: " + str(len(self.vectors)) + "\n"
        s += "\n"
        s += "Bloch sphere properties:\n"
        s += "------------------------\n"
        s += "font_color:      " + str(self.font_color) + "\n"
        s += "font_size:       " + str(self.font_size) + "\n"
        s += "frame_alpha:     " + str(self.frame_alpha) + "\n"
        s += "frame_color:     " + str(self.frame_color) + "\n"
        s += "frame_width:     " + str(self.frame_width) + "\n"
        s += "point_color:     " + str(self.point_color) + "\n"
        s += "point_marker:    " + str(self.point_marker) + "\n"
        s += "point_size:      " + str(self.point_size) + "\n"
        s += "sphere_alpha:    " + str(self.sphere_alpha) + "\n"
        s += "sphere_color:    " + str(self.sphere_color) + "\n"
        s += "figsize:         " + str(self.figsize) + "\n"
        s += "vector_color:    " + str(self.vector_color) + "\n"
        s += "vector_width:    " + str(self.vector_width) + "\n"
        s += "vector_style:    " + str(self.vector_style) + "\n"
        s += "vector_mutation: " + str(self.vector_mutation) + "\n"
        s += "view:            " + str(self.view) + "\n"
        s += "xlabel:          " + str(self.xlabel) + "\n"
        s += "xlpos:           " + str(self.xlpos) + "\n"
        s += "ylabel:          " + str(self.ylabel) + "\n"
        s += "ylpos:           " + str(self.ylpos) + "\n"
        s += "zlabel:          " + str(self.zlabel) + "\n"
        s += "zlpos:           " + str(self.zlpos) + "\n"
        return s

    def _repr_png_(self):
        from IPython.core.pylabtools import print_figure
        self.render()
        fig_data = print_figure(self.fig, 'png')
        plt.close(self.fig)
        return fig_data

    def _repr_svg_(self):
        from IPython.core.pylabtools import print_figure
        self.render()
        fig_data = print_figure(self.fig, 'svg').decode('utf-8')
        plt.close(self.fig)
        return fig_data

    def clear(self):
        """Resets Bloch sphere data sets to empty.
        """
        self.points = []
        self.vectors = []
        self.point_style = []
        self.annotations = []

    def add_points(self, points, meth='s'):
        """Add a list of data points to bloch sphere.

        Parameters
        ----------
        points : array_like
            Collection of data points.

        meth : {'s', 'm', 'l'}
            Type of points to plot, use 'm' for multicolored, 'l' for points
            connected with a line.
        """
        if not isinstance(points[0], (list, ndarray)):
            points = [[points[0]], [points[1]], [points[2]]]
        points = array(points)
        if meth == 's':
            if len(points[0]) == 1:
                pnts = array([[points[0][0]], [points[1][0]], [points[2][0]]])
                pnts = append(pnts, points, axis=1)
            else:
                pnts = points
            self.points.append(pnts)
            self.point_style.append('s')
        elif meth == 'l':
            self.points.append(points)
            self.point_style.append('l')
        else:
            self.points.append(points)
            self.point_style.append('m')

    def add_states(self, state, kind='vector'):
        """Add a state vector Qobj to Bloch sphere.

        Parameters
        ----------
        state : Qobj
            Input state vector.

        kind : {'vector', 'point'}
            Type of object to plot.
        """
        if isinstance(state, Qobj):
            state = [state]

        for st in state:
            vec = [expect(sigmax(), st),
                   expect(sigmay(), st),
                   expect(sigmaz(), st)]

            if kind == 'vector':
                self.add_vectors(vec)
            elif kind == 'point':
                self.add_points(vec)

    def add_vectors(self, vectors):
        """Add a list of vectors to Bloch sphere.

        Parameters
        ----------
        vectors : array_like
            Array with vectors of unit length or smaller.
        """
        if isinstance(vectors[0], (list, ndarray)):
            for vec in vectors:
                self.vectors.append(vec)
        else:
            self.vectors.append(vectors)

    def add_annotation(self, state_or_vector, text, **kwargs):
        """
        Add a text or LaTeX annotation to Bloch sphere, parametrized by a qubit
        state or a vector.

        Parameters
        ----------
        state_or_vector : Qobj/array/list/tuple
            Position for the annotaion.
            Qobj of a qubit or a vector of 3 elements.

        text : str
            Annotation text.
            You can use LaTeX, but remember to use raw string
            e.g. r"$\\langle x \\rangle$"
            or escape backslashes
            e.g. "$\\\\langle x \\\\rangle$".

        kwargs :
            Options as for mplot3d.axes3d.text, including:
            fontsize, color, horizontalalignment, verticalalignment.

        """
        if isinstance(state_or_vector, Qobj):
            vec = [expect(sigmax(), state_or_vector),
                   expect(sigmay(), state_or_vector),
                   expect(sigmaz(), state_or_vector)]
        elif isinstance(state_or_vector, (list, ndarray, tuple)) \
                and len(state_or_vector) == 3:
            vec = state_or_vector
        else:
            raise Exception("Position needs to be specified by a qubit " +
                            "state or a 3D vector.")
        self.annotations.append({'position': vec,
                                 'text': text,
                                 'opts': kwargs})

    def add_arc(self, start_angle, end_angle, radius=1.0, dir='z',
                z_angle=0, label=None, arrowhead=False, arrowhead_pos=100,
                capstyle='butt', **kwargs):
        """
        Add an arc to Bloch sphere

        Parameters
        ----------
        start_angle : float
            Start angle of the arc in its plane.
        end_angle : float
            End angle of the arc in its plane.
        radius : float
            Radius of the arc.
        dir : str
            Direction perpendicular to the arc ('x', 'y' or 'z').
        z_angle : float
            Rotation angle around z-axis.
        label : str
            Annotation text.
            You can use LaTeX, but remember to use raw string
            e.g. r"$\\theta$"
            or escape backslashes
            e.g. "$\\\\theta$".
        arrowhead : bool
            If true, an arrow head will be drawn.
        arrowhead_pos : float/int
            Position of the arrow head along the arc in percentage.
        capstyle : str
            Line cap style ('butt', 'round' or 'projection').

        kwargs :
            Options as for mplot3d.axes3d.text, including:
            fontsize, color, horizontalalignment, verticalalignment.

        """
        if arrowhead_pos == 100:
            self.arcs.append({**{'start_angle': start_angle,
                                 'end_angle': end_angle,
                                 'radius': radius, 'dir': dir,
                                 'z_angle': z_angle, 'label': label,
                                 'arrowhead': arrowhead,
                                 'capstyle': capstyle}, **kwargs})
        else:
            mid_angle = (arrowhead_pos/100)*(end_angle-start_angle)
            mid_angle += start_angle
            if arrowhead_pos < 50:
                label_1, label_2 = label, ''
            else:
                label_1, label_2 = '', label
            self.arcs.append({**{'start_angle': mid_angle,
                                 'end_angle': end_angle,
                                 'radius': radius, 'dir': dir,
                                 'z_angle': z_angle, 'label': label_1,
                                 'arrowhead': False,
                                 'capstyle': capstyle}, **kwargs})
            self.arcs.append({**{'start_angle': start_angle,
                                 'end_angle': mid_angle,
                                 'radius': radius, 'dir': dir,
                                 'z_angle': z_angle, 'label': label_2,
                                 'arrowhead': arrowhead,
                                 'capstyle': capstyle}, **kwargs})
        
    def add_projection(self, x, y, z, x_label='', y_label='', z_label='',
                       xy=False, offset=0.2, **kwargs):
        """
        Add a projection to Bloch sphere

        Parameters
        ----------
        x : float
            x coordinate of the point to project on the xy plane.
        y : float
            y coordinate of the point to project on the xy plane.
        z : float
            z coordinate of the point to project on the xy plane.
        x_label : str
            Label of the x-axis projection.
        y_label : str
            Label of the y-axis projection.
        z_label : str
            Label of the z-axis projection.
        xy : bool
            If true, the xy projections will be drawn.
        offset : float

        kwargs :
            Options as for mplot3d.axes3d.text, including:
            fontsize, color, horizontalalignment, verticalalignment.

        """
        self.projections.append({**{'x': x, 'y': y, 'z': z,
                                    'x_label': x_label,
                                    'y_label': y_label,
                                    'z_label': z_label,
                                    'xy': xy, 'offset': offset},
                                    **kwargs})
        
    def add_trajectory(self, xs, ys, zs, arrowhead=False,
                       arrowhead_pos=100, capstyle='butt',
                       style='', **kwargs):
        """
        Add a trajectory to Bloch sphere

        Parameters
        ----------
        arrowhead : bool
            If true, an arrow head will be drawn.
        arrowhead_pos : float/int
            Position of the arrow head along the arc in percentage.
        capstyle : str
            Line cap style ('butt', 'round' or 'projection').
        style : str
            Line style.

        kwargs :
            Options as for mplot3d.axes3d.text, including:
            fontsize, color, horizontalalignment, verticalalignment.

        """
        style = style or self.trajectory_style
        if arrowhead_pos == 100:
            self.trajectories.append({**{'xs': xs, 'ys': ys, 'zs': zs,
                                         'arrowhead': arrowhead,
                                         'capstyle': capstyle,
                                         'style': style}, **kwargs})
        else:
            mid = int(round(len(xs)*arrowhead_pos/100))
            self.trajectories.append({**{'xs': xs[mid-1:], 'ys': ys[mid-1:],
                                         'zs': zs[mid-1:], 'arrowhead': False,
                                         'capstyle': capstyle,
                                         'style': style}, **kwargs})
            self.trajectories.append({**{'xs': xs[:mid], 'ys': ys[:mid],
                                         'zs': zs[:mid], 'arrowhead': arrowhead,
                                         'capstyle': capstyle,
                                         'style': style}, **kwargs})

    def make_sphere(self):
        """
        Plots Bloch sphere and data sets.
        """
        self.render(self.fig, self.axes)

    def run_from_ipython(self):
        try:
            __IPYTHON__
            return True
        except NameError:
            return False

    def render(self, fig=None, axes=None):
        """
        Render the Bloch sphere and its data sets in on given figure and axes.
        """
        if self._rendered:
            self.axes.clear()

        self._rendered = True

        # Figure instance for Bloch sphere plot
        if not fig:
            self.fig = plt.figure(figsize=self.figsize)

        if not axes:
            self.axes = _axes3D(self.fig, azim=self.view[0],
                                elev=self.view[1])

        if self.background:
            self.axes.clear()
            self.axes.set_xlim3d(-1.3, 1.3)
            self.axes.set_ylim3d(-1.3, 1.3)
            self.axes.set_zlim3d(-1.3, 1.3)
        else:
            self.plot_axes()
            self.axes.set_axis_off()
            self.axes.set_xlim3d(-0.7, 0.7)
            self.axes.set_ylim3d(-0.7, 0.7)
            self.axes.set_zlim3d(-0.7, 0.7)
        # Manually set aspect ratio to fit a square bounding box.
        # Matplotlib did this stretching for < 3.3.0, but not above.
        if parse_version(matplotlib.__version__) >= parse_version('3.3'):
            self.axes.set_box_aspect((1, 1, 1))

        self.axes.grid(False)
        self.plot_back()
        self.plot_arcs()
        self.plot_projections()
        self.plot_trajectories()
        self.plot_points()
        self.plot_vectors()
        self.plot_front()
        self.plot_axes_labels()
        self.plot_annotations()

    def plot_back(self):
        # back half of sphere
        u = linspace(0, pi, 25)
        v = linspace(0, pi, 25)
        x = outer(cos(u), sin(v))
        y = outer(sin(u), sin(v))
        z = outer(ones(size(u)), cos(v))
        self.axes.plot_surface(x, y, z, rstride=2, cstride=2,
                               color=self.sphere_color, linewidth=0,
                               alpha=self.sphere_alpha)
        # wireframe
        self.axes.plot_wireframe(x, y, z, rstride=4, cstride=4,
                                 color=self.frame_color,
                                 alpha=self.frame_alpha)
        # equators
        if 'z' in self.equators_back:
            self.axes.plot(1.0 * cos(u), 1.0 * sin(u), zs=0, zdir='z',
                        lw=self.frame_width, color=self.frame_color)
        if 'y' in self.equators_back:
            self.axes.plot(1.0 * cos(u), 1.0 * sin(u), zs=0, zdir='y',
                        lw=self.frame_width, color=self.frame_color)
        if 'x' in self.equators_back:
            self.axes.plot(1.0 * cos(u), 1.0 * sin(u), zs=0, zdir='x',
                        lw=self.frame_width, color=self.frame_color)

    def plot_front(self):
        # front half of sphere
        u = linspace(-pi, 0, 25)
        v = linspace(0, pi, 25)
        x = outer(cos(u), sin(v))
        y = outer(sin(u), sin(v))
        z = outer(ones(size(u)), cos(v))
        self.axes.plot_surface(x, y, z, rstride=2, cstride=2,
                               color=self.sphere_color, linewidth=0,
                               alpha=self.sphere_alpha)
        # wireframe
        self.axes.plot_wireframe(x, y, z, rstride=4, cstride=4,
                                 color=self.frame_color,
                                 alpha=self.frame_alpha)
        # equators
        if 'z' in self.equators_front:
            self.axes.plot(1.0 * cos(u), 1.0 * sin(u),
                        zs=0, zdir='z', lw=self.frame_width,
                        color=self.frame_color)
        if 'y' in self.equators_front:
            self.axes.plot(1.0 * cos(u), 1.0 * sin(u),
                        zs=0, zdir='y', lw=self.frame_width,
                        color=self.frame_color)
        if 'x' in self.equators_front:
            self.axes.plot(1.0 * cos(u), 1.0 * sin(u),
                        zs=0, zdir='x', lw=self.frame_width,
                        color=self.frame_color)

    def plot_axes(self):
        # axes
        span = linspace(-1.0, 1.0, 2)
        self.axes.plot(span, 0 * span, zs=0, zdir='z', label='X',
                       lw=self.frame_width, color=self.frame_color)
        self.axes.plot(0 * span, span, zs=0, zdir='z', label='Y',
                       lw=self.frame_width, color=self.frame_color)
        self.axes.plot(0 * span, span, zs=0, zdir='y', label='Z',
                       lw=self.frame_width, color=self.frame_color)

    def plot_axes_labels(self):
        # axes labels
        opts = {'fontsize': self.font_size,
                'color': self.font_color,
                'horizontalalignment': 'center',
                'verticalalignment': 'center'}
        self.axes.text(0, -self.xlpos[0], 0, self.xlabel[0], **opts)
        self.axes.text(0, -self.xlpos[1], 0, self.xlabel[1], **opts)

        self.axes.text(self.ylpos[0], 0, 0, self.ylabel[0], **opts)
        self.axes.text(self.ylpos[1], 0, 0, self.ylabel[1], **opts)

        self.axes.text(0, 0, self.zlpos[0], self.zlabel[0], **opts)
        self.axes.text(0, 0, self.zlpos[1], self.zlabel[1], **opts)

        for a in (self.axes.w_xaxis.get_ticklines() +
                  self.axes.w_xaxis.get_ticklabels()):
            a.set_visible(False)
        for a in (self.axes.w_yaxis.get_ticklines() +
                  self.axes.w_yaxis.get_ticklabels()):
            a.set_visible(False)
        for a in (self.axes.w_zaxis.get_ticklines() +
                  self.axes.w_zaxis.get_ticklabels()):
            a.set_visible(False)

    def plot_vectors(self):
        # -X and Y data are switched for plotting purposes
        for k in range(len(self.vectors)):

            xs3d = self.vectors[k][1] * array([0, 1])
            ys3d = -self.vectors[k][0] * array([0, 1])
            zs3d = self.vectors[k][2] * array([0, 1])

            color = self.vector_color[mod(k, len(self.vector_color))]

            if self.vector_style == '':
                # simple line style
                self.axes.plot(xs3d, ys3d, zs3d,
                               zs=0, zdir='z', label='Z',
                               lw=self.vector_width, color=color)
            else:
                # decorated style, with arrow heads
                a = Arrow3D(xs3d, ys3d, zs3d,
                            mutation_scale=self.vector_mutation,
                            lw=self.vector_width,
                            arrowstyle=self.vector_style,
                            color=color)

                self.axes.add_artist(a)

    def plot_points(self):
        # -X and Y data are switched for plotting purposes
        for k in range(len(self.points)):
            num = len(self.points[k][0])
            dist = [sqrt(self.points[k][0][j] ** 2 +
                         self.points[k][1][j] ** 2 +
                         self.points[k][2][j] ** 2) for j in range(num)]
            if any(abs(dist - dist[0]) / dist[0] > 1e-12):
                # combine arrays so that they can be sorted together
                zipped = list(zip(dist, range(num)))
                zipped.sort()  # sort rates from lowest to highest
                dist, indperm = zip(*zipped)
                indperm = array(indperm)
            else:
                indperm = arange(num)
            if self.point_style[k] == 's':
                self.axes.scatter(
                    real(self.points[k][1][indperm]),
                    - real(self.points[k][0][indperm]),
                    real(self.points[k][2][indperm]),
                    s=self.point_size[mod(k, len(self.point_size))],
                    alpha=1,
                    edgecolor=None,
                    zdir='z',
                    color=self.point_color[mod(k, len(self.point_color))],
                    marker=self.point_marker[mod(k, len(self.point_marker))])

            elif self.point_style[k] == 'm':
                pnt_colors = array(self.point_color *
                                   int(ceil(num / float(len(self.point_color)))))

                pnt_colors = pnt_colors[0:num]
                pnt_colors = list(pnt_colors[indperm])
                marker = self.point_marker[mod(k, len(self.point_marker))]
                s = self.point_size[mod(k, len(self.point_size))]
                self.axes.scatter(real(self.points[k][1][indperm]),
                                  -real(self.points[k][0][indperm]),
                                  real(self.points[k][2][indperm]),
                                  s=s, alpha=1, edgecolor=None,
                                  zdir='z', color=pnt_colors,
                                  marker=marker)

            elif self.point_style[k] == 'l':
                color = self.point_color[mod(k, len(self.point_color))]
                self.axes.plot(real(self.points[k][1]),
                               -real(self.points[k][0]),
                               real(self.points[k][2]),
                               alpha=0.75, zdir='z',
                               color=color)

    def plot_annotations(self):
        # -X and Y data are switched for plotting purposes
        for annotation in self.annotations:
            vec = annotation['position']
            opts = {'fontsize': self.font_size,
                    'color': self.font_color,
                    'horizontalalignment': 'center',
                    'verticalalignment': 'center'}
            opts.update(annotation['opts'])
            self.axes.text(vec[1], -vec[0], vec[2],
                           annotation['text'], **opts)

    def plot_arcs(self):
        swap = {'x': 'y', 'y': 'x', 'z': 'z'}
        for k, arc in enumerate(self.arcs):
            angle_degrees = abs(arc['end_angle']-arc['start_angle']) / pi * 180
            n_points = int(round(angle_degrees))
            u = linspace(arc['start_angle'], arc['end_angle'], n_points)
            u = array([*u, u[-1]+(u[-1]-u[-2])])
            n_points += 1
            xs = arc['radius'] * cos(u)
            ys = arc['radius'] * sin(u)
            color = self.arc_color[mod(k, len(self.arc_color))]
            c, s = cos(arc['z_angle']), sin(arc['z_angle'])
            rot = array(((c, -s), (s, c)))
            
            if swap[arc['dir']] == 'x':
                a, b = rot.dot(array([[0]*n_points, -xs]))
                self.axes.plot(a[:-1], b[:-1], zs=ys[:-1],
                               lw=self.arc_width, color=color,
                               solid_capstyle=arc.get('capstyle'),
                               dash_capstyle=arc.get('capstyle'))
                xs3d = array([a[-3], a[-1]])
                ys3d = array([b[-3], b[-1]])
                zs3d = array([ys[-3], ys[-1]])
            if swap[arc['dir']] == 'y':
                a, b = rot.dot(array([xs, [0]*n_points]))
                self.axes.plot(a[:-1], b[:-1], zs=ys[:-1],
                               lw=self.arc_width, color=color,
                               solid_capstyle=arc.get('capstyle'),
                               dash_capstyle=arc.get('capstyle'))
                xs3d = array([a[-3], a[-1]])
                ys3d = array([b[-3], b[-1]])
                zs3d = array([ys[-3], ys[-1]])
            if swap[arc['dir']] == 'z':
                self.axes.plot(ys[:-1], -xs[:-1], zs=0,
                               lw=self.arc_width, color=color,
                               solid_capstyle=arc.get('capstyle'),
                               dash_capstyle=arc.get('capstyle'))
                xs3d = array([ys[-3], ys[-1]])
                ys3d = array([-xs[-3], -xs[-1]])
                zs3d = array([0, 0])
            
            if arc.get('arrowhead'):
                a = Arrow3D(xs3d, ys3d, zs3d,
                            mutation_scale=self.vector_mutation,
                            lw=self.vector_width,
                            arrowstyle=self.vector_style,
                            color=color, shrinkA=0, shrinkB=0)
                
                self.axes.add_artist(a)
            
            if arc.get('label'):
                xs = (arc['radius']+0.2) * cos(u)
                ys = (arc['radius']+0.2) * sin(u)
                opts = {'fontsize': self.font_size,
                        'color': self.font_color,
                        'horizontalalignment': 'center',
                        'verticalalignment': 'center'}
                
                if swap[arc['dir']] == 'x':
                    a, b = rot.dot(array([0, -xs[n_points//2]]))
                    self.axes.text(a, b, ys[n_points//2],
                                   arc['label'], **opts)
                if swap[arc['dir']] == 'y':
                    a, b = rot.dot(array([xs[n_points//2], 0]))
                    self.axes.text(a, b, ys[n_points//2],
                                   arc['label'], **opts)
                if swap[arc['dir']] == 'z':
                    self.axes.text(ys[n_points//2], -xs[n_points//2], 0,
                                   arc['label'], **opts)
                    
    def plot_projections(self):
        for k, projection in enumerate(self.projections):
            x, y, z, x_lbl, y_lbl, z_lbl, xy, offset = (
                projection.get('x'), projection.get('y'),
                projection.get('z'), projection.get('x_label'),
                projection.get('y_label'), projection.get('z_label'),
                projection.get('xy'), projection.get('offset'))
            color = self.projection_color[mod(k, len(self.projection_color))]
            opts = {'color': color,
                    'lw': self.projection_width,
                    'ls': self.projection_style}
            self.axes.plot([*linspace(0, x, 100)] + [x]*100,
                           [*linspace(0, y, 100)] + [y]*100,
                           [0]*100 + [*linspace(0, z, 100)],
                           solid_capstyle='butt', dash_capstyle='butt', **opts)
            if z_lbl:
                t = offset/sqrt(x**2+y**2)
                self.add_annotation([-y*(1+t), x*(1+t), z/2], z_lbl)
            if xy:
                self.axes.plot([*linspace(0, x, 100)] + [x]*100,
                               [y]*100 + [*linspace(y, 0, 100)],
                               [0]*200, solid_capstyle='butt',
                               dash_capstyle='butt', **opts)
                if x_lbl:
                    self.add_annotation([-y/2, x+offset*sign(x), 0], x_lbl)
                if y_lbl:
                    self.add_annotation([-y-offset*sign(y), x/2, 0], y_lbl)
                    
    def plot_trajectories(self):
        for k, trajectory in enumerate(self.trajectories):
            color = self.trajectory_color[mod(k, len(self.trajectory_color))]
            opts = {'color': color,
                    'lw': self.trajectory_width,
                    'ls': trajectory.get('style')}
            xs = array(trajectory.get('xs'))
            ys = array(trajectory.get('ys'))
            zs = array(trajectory.get('zs'))
            self.axes.plot(ys, -xs, zs, **opts,
                           solid_capstyle=trajectory.get('capstyle'),
                           dash_capstyle=trajectory.get('capstyle'))
            if trajectory.get('arrowhead'):
                a = Arrow3D(ys[-2:], -xs[-2:], zs[-2:],
                            mutation_scale=self.vector_mutation,
                            lw=self.vector_width,
                            arrowstyle=self.vector_style,
                            color=color, shrinkA=0, shrinkB=0)
                self.axes.add_artist(a)

    def show(self):
        """
        Display Bloch sphere and corresponding data sets.
        """
        self.render(self.fig, self.axes)
        if self.run_from_ipython():
            if self._shown:
                display(self.fig)
        else:
            self.fig.show()
        self._shown = True

    def save(self, name=None, format='png', dirc=None, dpin=None):
        """Saves Bloch sphere to file of type ``format`` in directory ``dirc``.

        Parameters
        ----------

        name : str
            Name of saved image. Must include path and format as well.
            i.e. '/Users/Paul/Desktop/bloch.png'
            This overrides the 'format' and 'dirc' arguments.
        format : str
            Format of output image.
        dirc : str
            Directory for output images. Defaults to current working directory.
        dpin : int
            Resolution in dots per inch.

        Returns
        -------
        File containing plot of Bloch sphere.

        """
        self.render(self.fig, self.axes)
        # Conditional variable for first argument to savefig
        # that is set in subsequent if-elses
        complete_path = ""
        if dirc:
            if not os.path.isdir(os.getcwd() + "/" + str(dirc)):
                os.makedirs(os.getcwd() + "/" + str(dirc))
        if name is None:
            if dirc:
                complete_path = os.getcwd() + "/" + str(dirc) + '/bloch_' \
                                + str(self.savenum) + '.' + format
            else:
                complete_path = os.getcwd() + '/bloch_' + \
                                str(self.savenum) + '.' + format
        else:
            complete_path = name

        if dpin:
            self.fig.savefig(complete_path, dpi=dpin)
        else:
            self.fig.savefig(complete_path)
        self.savenum += 1
        if self.fig:
            plt.close(self.fig)


def _hide_tick_lines_and_labels(axis):
    '''
    Set visible property of ticklines and ticklabels of an axis to False
    '''
    for a in axis.get_ticklines() + axis.get_ticklabels():
        a.set_visible(False)
