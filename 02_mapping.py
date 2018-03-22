
import pandas as pd
from bokeh.io import output_file, show
from bokeh.models import (GMapPlot, GMapOptions, HoverTool, Range1d, 
    ColumnDataSource, Circle, PanTool, WheelZoomTool, ImageURL, 
    TapTool, ResetTool, SaveTool, OpenURL, Title)



### Config
import api_keys
df = pd.read_csv('embassy_locations.csv')



### Set Up Plot
output_file("embassy.html")

# Thank you to StipeP @
# https://snazzymaps.com/style/8097/wy
style = '''
        [{"featureType": "all", "elementType": "geometry.fill", "stylers": [{"weight": "2.00"}]},
        {"featureType": "all", "elementType": "geometry.stroke", "stylers": [{"color": "#9c9c9c"}]},
        {"featureType": "all", "elementType": "labels.text", "stylers": [{"visibility": "on"}]},
        {"featureType": "landscape", "elementType": "all", "stylers": [{"color": "#f2f2f2"}]},
        {"featureType": "landscape", "elementType": "geometry.fill", "stylers": [{"color": "#f9f9f9"}]},
        {"featureType": "landscape.man_made", "elementType": "geometry.fill", "stylers": [{"color": "#f9f9f9"}]},
        {"featureType": "poi", "elementType": "all", "stylers": [{"visibility": "off"}]},
        {"featureType": "road", "elementType": "all", "stylers": [{"saturation": -100}, {"lightness": 45}]},
        {"featureType": "road", "elementType": "geometry.fill", "stylers": [{"color": "#eeeeee"}]},
        {"featureType": "road","elementType": "labels.text.fill","stylers": [{"color": "#7b7b7b"}]},
        {"featureType": "road", "elementType": "labels.text.stroke", "stylers": [{"color": "#ffffff"}]},
        {"featureType": "road.highway", "elementType": "all", "stylers": [{"visibility": "simplified"}]},
        {"featureType": "road.arterial", "elementType": "labels.icon", "stylers": [{"visibility": "off"}]},
        {"featureType": "transit", "elementType": "all", "stylers": [{"visibility": "off"}]},
        {"featureType": "water", "elementType": "all", "stylers": [{"color": "#46bcec"}, {"visibility": "on"}]},
        {"featureType": "water", "elementType": "geometry.fill", "stylers": [{"color": "#c8d7d4"}]},
        {"featureType": "water", "elementType": "labels.text.fill", "stylers": [{"color": "#070707"}]},
        {"featureType": "water", "elementType": "labels.text.stroke", "stylers": [{"color": "#ffffff"}]}]
        '''


map_options = GMapOptions(lat=38.925821, lng=-77.050819, map_type="roadmap", zoom=13, styles=style)
plot = GMapPlot(
    x_range=Range1d(), y_range=Range1d(), map_options=map_options)

plot.api_key = api_keys.google
plot.add_layout(Title(text="Diplomatic Missions in DC", align="center", text_font_size='14pt'), "above")
plot.add_layout(Title(text="Clicking on an embassy will bring you to its website. The quality of embassy websites varies.", align="left", text_font_size='10pt'), "below")

source = ColumnDataSource(data=dict(
        lat = df['lat'], 
        lng = df['lng'],
        imgs = df['Image_url'],
        name = df['Embassy'],
        imgs_ht = df['Image_height'],
        imgs_wd = df['Image_width'],
        addr = df['Location'],
        flag = df['Flag_url'],
        flag_ht = df['Flag_height'],
        flag_wd = df['Flag_width'],
        embassy_url = df['Reference_url']
))



### Plot Locations
circle = Circle(x="lng", y="lat", size=5, fill_color='Blue', line_color=None)
plot.add_glyph(source, circle, name='Points')

renderer = plot.select(name='Points')
renderer.selection_glyph = Circle(fill_alpha=1, fill_color='firebrick', line_alpha = 1, line_color='firebrick')
renderer.nonselection_glyph = Circle(fill_alpha=0.2, fill_color='blue', line_alpha = 0.2, line_color='blue')
renderer.hover_glyph = Circle(fill_alpha=1, fill_color='firebrick', line_alpha = 1, line_color='firebrick')
renderer.level='image'


### Plot Flags
flags = ImageURL(url='flag', x='lng', y='lat', anchor='bottom_left', global_alpha=0.7)
plot.add_glyph(source, flags, name='Flags')
renderer2 = plot.select(name='Flags')
renderer2.selection_glyph = ImageURL(url='flag', x='lng', y='lat', anchor='bottom_left', global_alpha=0.7)
renderer2.nonselection_glyph = ImageURL(url='flag', x='lng', y='lat', anchor='bottom_left', global_alpha=0.2)
renderer2.level='overlay'

plot.legend.location = "top_left"
plot.legend.click_policy="hide"

### Plot Tools
hover = HoverTool(tooltips="""
    <div>
        <div>
            <img
                src="@imgs" height="@imgs_ht" alt="@imgs" width="@imgs_wd"
                style="float: left; margin: 0px 15px 15px 0px;"
                border="1"
            ></img>
        </div>
        <div>
            <img
                src="@flag" height="@flag_ht" alt="@imgs" width="@flag_wd"
            ></img>
            <span style="font-size: 14px; font-weight: bold;">@name</span>
        </div>
        <div>
            <span style="font-size: 10px: bold;">@addr</span>
        </div>
    </div>
    """
    )

wheel_zoom = WheelZoomTool()

tap = TapTool()
tap.renderers = []
tap.callback = OpenURL(url='@embassy_url')

plot.add_tools(PanTool(), wheel_zoom, hover, tap, ResetTool(), SaveTool())
plot.toolbar.active_scroll = wheel_zoom



### Export
show(plot)

