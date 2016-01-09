__all__=['Fiddle']

from IPython.display import HTML, display, clear_output
import uuid

from jinja2 import (Template, DebugUndefined)

import lesscpy
from six import StringIO


class Fiddle(object):
    def __init__(self, html='', css='', div_css='', js='', jslibs=tuple(), csslibs=tuple(),
                 extra_vars=dict()):
        self.html = html
        self.css = css
        self.div_css = div_css
        self.js = js
        self.jslibs = jslibs
        self.csslibs = csslibs
        self.extra_vars = extra_vars
        
    def _repr_html_(self):
        return self._to_html_()
        
    def _to_html_(self):
        
        div_id = u'i' + unicode(uuid.uuid4())
        
        HTML_ = Template(u"""<div id="{{div_id}}">
    {{html}}
</div>
""").render(div_id=div_id, html=self.html)
        
        # compute nested css
        div_css_wrapped = Template(
        """
           #{{div_id}} { {{div_css}} }
        """).render(div_id=div_id, div_css=self.div_css)
            
        div_css_expanded = lesscpy.compile(StringIO(div_css_wrapped), minify=True)
        
        CSS = Template(u"""<style type="text/css">
{{css}}

{{div_css_expanded}}
</style>
""").render(css=self.css, div_css_expanded=div_css_expanded)
        
        # JS
        JS = u"""
<script type="text/javascript">

    {% if csslibs %}
    // load css if it's not already there: http://stackoverflow.com/a/4724676/7782
    function loadcss(url) {
        if (!$("link[href='" + url + "']").length)
            $('<link href="' + url + '" rel="stylesheet">').appendTo("head");
    }
    {% endif %}
    
    {% for item in csslibs %}
    loadcss('{{item}}');
    {% endfor %}
    

    require.config({
          paths: {
             {% for item in jslibs %}
               '{{item.0}}': "{{item.1}}", 
             {% endfor %}
          }
    });

     
    require({{jslibs_names}}, function({{jslibs_objs}}) {
   
        (function(){
 
        var element = $('#{{div_id}}');
""" + self.js +  u"""
   
       })(); 
    });

</script>
"""
        
        template = Template(HTML_ + CSS + JS)
        return template.render(div_id=div_id,
                     csslibs = self.csslibs,
                     jslibs = self.jslibs,
                     jslibs_names = "[{}]".format(",".join(['"{}"'.format(jslib[0]) for jslib in self.jslibs])), 
                     jslibs_objs = ",".join([jslib[2] for jslib in self.jslibs]),
                     **self.extra_vars
                    )

    
