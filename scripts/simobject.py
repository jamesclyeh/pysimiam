from math import sin, cos
import pylygon
from pose import Pose

class SimObject:
    """The base class for creating drawn objects in the simulator. 
Posses both a Pose object and a color"""

    def __init__(self, pose, color = 0):
        self.set_color(color)
        self.set_pose(pose)

    def get_color(self):
        """gets the color"""
        return self.__color
    
    def set_color(self, color):
        """sets the color"""
        self.__color = color

    def get_pose(self):
        """Returns the pose of the object in world coordinates
        """
        return self.__pose

    def set_pose(self,pose):
        """Returns the pose of the object in world coordinates
        """
        self.__world_envelope = None
        self.__pose = pose

    def draw(self,dc):
        """Draws the object on the passed DC
        """
        pass
    
    def get_envelope(self):
        """The envelope of the object in object's local coordinates
        """
        ## At the moment the proposed format is a list of points
        pass
    
    def get_world_envelope(self, recalculate=False):
        """gets the envelop for checking collision"""
        if self.__world_envelope is None or recalculate:
            x,y,t = self.get_pose()
            self.__world_envelope = [(x+p[0]*cos(t)-p[1]*sin(t),
                                      y+p[0]*sin(t)+p[1]*cos(t))
                                     for p in self.get_envelope()]
        return self.__world_envelope
    
    def get_bounding_rect(self):
        """Get the smallest rectangle that contains the object
        Returns a tuple (x,y,width,height)
        """
        xmin, ymin, xmax, ymax = self.get_bounds()
        return (xmin,ymin,xmax-xmin,ymax-ymin)
    
    def has_collision(self, other):
        """Check if the object has collided with other.
        Return True or False"""
        self_poly = pylygon.Polygon(self.get_world_envelope())
        other_poly = pylygon.Polygon(other.get_world_envelope())
        
        # TODO: use distance() for performance
        #print "Dist:", self_poly.distance(other_poly)
        
        collision = self_poly.collidepoly(other_poly)
        if isinstance(collision, bool):
            if not collision: return False
        
        # Test code - print out collisions
        #print "Collision between {} and {}".format(self, other)
        # end of test code
        
        return True
    
    def get_contact_points(self, other):
        """Get a list of contact points with other object
        Retrun a list of (x, y)"""
        self_poly = pylygon.Polygon(self.get_world_envelope())
        other_poly = pylygon.Polygon(other.get_world_envelope())
        return self_poly.intersection_points(other_poly)

    def get_bounds(self):
        """Get the smallest rectangle that contains the object.
        Returns a tuple (xmin,ymin,xmax,ymax)"""
        xs, ys = zip(*self.get_world_envelope())
        return (min(xs), min(ys), max(xs), max(ys))
            

class Polygon(SimObject):
    """The polygon simobject is used to draw objects in the world"""
    def __init__(self, pose, shape, color):
        SimObject.__init__(self,pose, color)
        self.__shape = shape

    def get_envelope(self):
        return self.__shape

    def draw(self,r):
        r.set_pose(self.get_pose())
        r.set_brush(self.get_color())
        r.draw_polygon(self.get_envelope())

class Path(SimObject):
    """The path is used to track the history of robot motion"""
    def __init__(self,start,color):
        SimObject.__init__(self, Pose(), color)
        self.points = [(start.x,start.y)]

    def reset(self,start):
        """sets teh start point to start.x and start.y"""
        self.points = [(start.x,start.y)]
        
    def add_point(self,pose):
        """adds a point to the chain of lines"""
        self.points.append((pose.x,pose.y))
        
    def draw(self,r):
        """draw the polyline from the line list"""
        r.set_pose(self.get_pose()) # Reset everything
        r.set_pen(self.get_color())
        for i in range(1,len(self.points)):
            x1,y1 = self.points[i-1]
            x2,y2 = self.points[i]
            r.draw_line(x1,y1,x2,y2)
        
