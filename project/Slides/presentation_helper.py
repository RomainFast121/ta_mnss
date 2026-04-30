#!/usr/bin/env python
################################################################

import base64
import sympy
import PyPDF2
import io
import IPython
from IPython.display import display
from IPython.display import HTML
import os
import fnmatch
import shutil
import subprocess
import matplotlib.pyplot as plt
import matplotlib.figure
from IPython.core.interactiveshell import InteractiveShell
from wand.image import Image as WImage
from wand.color import Color
from io import BytesIO
from tempfile import NamedTemporaryFile
from tempfile import mkdtemp
import ipyleaflet
from OSMPythonTools.nominatim import Nominatim
import numpy as np
import googlemaps
################################################################


def findImageFile(filename):
    if os.path.isfile(filename):
        return filename

    tool_dir = os.path.dirname(__file__)
    image_dir = os.path.join(tool_dir, '..', 'images')
    pattern = os.path.basename(filename)
    found = []
    for root, dirnames, filenames in os.walk(image_dir):
        for filename in fnmatch.filter(filenames, pattern):
            found.append(os.path.join(root, filename))

    if len(found) == 0:
        raise Exception("file not found: {0}".format(filename))
    if len(found) == 1:
        return found[0]

    raise Exception("Several files were found:\n{0}".format(found))


################################################################
def _print_latex_png(o):
    o = o._repr_latex_()
    dvioptions = None
    exprbuffer = BytesIO()
    # from IPython.core.debugger import Tracer
    # Tracer()()
    sympy.preview(o, output='png', viewer='BytesIO',
                  outputbuffer=exprbuffer, packages=('xcolor',),
                  dvioptions=dvioptions)
    return exprbuffer.getvalue()

################################################################


def _print_latex_svg(o):
    o = o._repr_latex_()
    dvioptions = None
    exprbuffer = BytesIO()
    # from IPython.core.debugger import Tracer
    # Tracer()()
    sympy.preview(o, output='svg', viewer='BytesIO',
                  outputbuffer=exprbuffer, packages=('xcolor',),
                  dvioptions=dvioptions)
    return exprbuffer.getvalue().decode()


################################################################


def registerFormatter(_type, _format, formatter_functor):
    f = InteractiveShell.instance().display_formatter.formatters[_format]
    f.for_type(_type, func=formatter_functor)

################################################################


def init_printing():
    sympy.init_printing()
    registerFormatter(IPython.core.display.Math,
                      'image/svg+xml', _print_latex_svg)
    registerFormatter(IPython.core.display.Math, 'image/png', _print_latex_png)

################################################################


VIDEO_TAG = """<video controls>
 <source src="data:video/x-m4v;base64,{0}" type="video/mp4">
 Your browser does not support the video tag.
</video>"""

VIDEO_TAG_width = """<video width="{1}" controls>
 <source src="data:video/x-m4v;base64,{0}" type="video/mp4">
 Your browser does not support the video tag.
</video>"""


def anim_to_html(anim, width=None):
    if not hasattr(anim, '_encoded_video'):
        with NamedTemporaryFile(suffix='.mp4') as f:
            anim.save(f.name, fps=1./(anim._interval*1e-3),
                      extra_args=['-vcodec', 'libx264',
                                  '-pix_fmt', 'yuv420p'])
            video = open(f.name, "rb").read()
        toto = base64.b64encode(video).decode()
        # print anim._encoded_video

    if width is not None:
        return VIDEO_TAG_width.format(toto, width)
    return VIDEO_TAG.format(toto)

################################################################


def display_video(filename, width=None):
    VIDEO_TAG = f"""<video controls>
 <source src="{filename}" type="video/mp4">
 Your browser does not support the video tag.
</video>"""

    VIDEO_TAG_width = f"""<video controls width="{width}">
 <source src="{filename}" type="video/mp4">
 Your browser does not support the video tag.
</video>"""

    if width is not None:
        video = VIDEO_TAG_width
    else:
        video = VIDEO_TAG

    return HTML(video)

################################################################


def display_embedded_video(filename, width=None):
    video = open(filename, "rb").read()
    video = base64.b64encode(video).decode()
    if width is not None:
        video = VIDEO_TAG_width.format(video, width)
    else:
        video = VIDEO_TAG.format(video)

    return HTML(video)

################################################################


def display_animation(anim, **kwargs):
    plt.close(anim._fig)
    return HTML(anim_to_html(anim, **kwargs))

################################################################


def display_images(objs, display_flag=True, **kwargs):
    htmls = [display_image(o, display_flag=False, **kwargs)
             for o in objs]

    width = 100/len(htmls)

    htmls_withdiv = ["" for h in htmls]
    for i, h in enumerate(htmls):
        htmls_withdiv[i] = '<div style="width:{0}%;'.format(width)
        if i == 0:
            htmls_withdiv[i] += 'float:left'
        if i == len(htmls) - 1:
            htmls_withdiv[i] += 'float:right'
        htmls_withdiv[i] += '"> {0} </div>'.format(h)
    html = '\n'.join(htmls_withdiv)
    html = '<div>' + html + '</div>'
    if display_flag:
        display(HTML(html))
    return html


def display_image(obj, resolution=200, width=None, height=None,
                  display_flag=True, center=False):

    if type(obj) == matplotlib.figure.Figure:
        png = InteractiveShell.instance().display_formatter.format(obj)

    elif type(obj) == str:
        try:
            fname = findImageFile(obj)

        except Exception as e:
            return str(e)

        img = WImage(filename=fname, resolution=resolution)
        img.trim()
        with Color('#FDFDFD') as white:
            twenty_percent = int(65535 * 0.2)
            img.transparent_color(white, alpha=0.0, fuzz=twenty_percent)

        if (width is None) and (height is None):
            display(img)
            return img

        png = InteractiveShell.instance().display_formatter.format(img)
    else:
        raise Exception('unknown obj type for an image')

    size_tag = ""
    if width is not None:
        size_tag += 'width="{0}"'.format(width)
    if height is not None:
        size_tag += 'height="{0}"'.format(height)

    data = png[0]['image/png']
    data = base64.b64encode(data).decode('utf-8')
    html = (r'<img alt="You cannot see the image with this browser/mailer" ' +
            r'src="data:image/png;base64,{0}"'.format(data))

    if size_tag != '':
        html += '{0}'.format(size_tag)
    html += '/>'

    if center:
        html = f'<center>{html}</center>'
    # print(html)
    if display_flag:
        display(HTML(html))
    return html

################################################################


def display_graph(obj, **kwargs):
    if not isinstance(obj, str):
        raise RuntimeError(
            'Graphs should be passed as a str object storing the graph'
            ' in dot format')

    with NamedTemporaryFile(suffix='.svg') as f:
        p = subprocess.Popen('dot -Tsvg -o' + f.name, shell=True,
                             stdin=subprocess.PIPE)
        p.communicate(input=obj.encode())
        display_image(f.name, **kwargs)

################################################################


def makeAnimationFromImageFiles(filenames, framerate=25, width=None):
    temp_dir = mkdtemp()
    ext = None
    for idx, f in enumerate(filenames):
        _dir = os.path.dirname(f)
        base = os.path.basename(f)
        base, _ext = os.path.splitext(base)
        ext = _ext
        if ext == '.pdf':
            _png = os.path.join(_dir, base+".png")
            subprocess.call('convert {0} {1}'.format(f, _png), shell=True)
            ext = ".png"
            f = _png
        new_name = "file{0:05d}{1}".format(idx, ext)
        new_name = os.path.join(temp_dir, new_name)
        # print base, ext
        # print new_name
        # print "copy {0} to {1}".format(f,new_name)
        shutil.copyfile(f, new_name)

    pattern = os.path.join(temp_dir, 'file%05d'+ext)
    with NamedTemporaryFile(suffix='.mp4') as f:
        cmd = ('ffmpeg -y -framerate {2} -i {0} -vf "scale=trunc(iw/2)*2:'
               'trunc(ih/2)*2" -c:v libx264 -r 30 '
               '-pix_fmt yuv420p {1}').format(pattern, f.name, framerate)
        p = subprocess.Popen(cmd, shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        p.wait()
        if p.returncode:
            out, err = p.communicate()
            print(out)
            print(err)
        video = open(f.name, "rb").read()
    toto = base64.b64encode(video).decode()

    shutil.rmtree(temp_dir)

    if width is not None:
        html = VIDEO_TAG_width.format(toto, width)
        HTML(html)
    return HTML(VIDEO_TAG.format(toto))


################################################################


def displayClassDiagram(classes, resolution=150,
                        width=None, height=None):

    png = makeClassDiagramImage(classes, resolution,
                                width, height)
    img = WImage(filename=png, resolution=resolution)
    with Color('#FDFDFD') as white:
        twenty_percent = int(65535 * 0.2)
        img.transparent_color(white, alpha=0.0, fuzz=twenty_percent)

    png = InteractiveShell.instance().display_formatter.format(img)

    size_tag = ""
    if width is not None:
        size_tag += 'width="{0}"'.format(width)
    if height is not None:
        size_tag += 'height="{0}"'.format(height)

    data = png[0]['image/png']
    html = (r'<img alt="You cannot see the image with this browser/mailer" '
            + 'src="data:image/png;base64,{0}" {1}/>'.format(
                base64.b64encode(data).decode('utf8'), size_tag))
    display(HTML(html))
    return html

################################################################


def makeClassDiagramImage(classes, resolution=150,
                          width=None, height=None):

    with NamedTemporaryFile(suffix='.classes', delete=False) as f:
        f.write(classes.encode('utf-8'))
        f.flush()

    fout = os.path.splitext(f.name)[0] + '.svg'
    _command = ('class_dumper_dot --collaboration_no '
                '-c {0} -o {1} -f svg'.format(f.name, fout))
    # print(_command)
    ret = subprocess.call(_command, shell=True)
    if ret:
        raise RuntimeError('could not launch commad:', _command)
    return fout

################################################################


def pdf_page_to_png(src_filename, pagenums=None, resolution=72):
    """
    Returns specified PDF page as wand.image.Image png.
    :param PyPDF2.PdfFileReader src_pdf: PDF from which to take pages.
    :param int pagenum: Page number to take.
    :param int resolution: Resolution for resulting png in DPI.
    """

    with open(src_filename, "rb") as f:
        src_pdf = PyPDF2.PdfFileReader(f)
        # print dir(src_pdf)
        # print src_pdf.numPages

    if pagenums is None:
        pagenums = [0]

    res = []
    for n in pagenums:
        dst_pdf = PyPDF2.PdfFileWriter()
        dst_pdf.addPage(src_pdf.getPage(n))

        pdf_bytes = io.BytesIO()
        dst_pdf.write(pdf_bytes)
        pdf_bytes.seek(0)

        img = WImage(file=pdf_bytes, resolution=resolution)
        img.convert("png")
        res.append(img)

    return res

################################################################
# maps stuff


def display_map(locations=[], zoom=5):

    center = np.array([0., 0.], dtype=float)
    for _, lat, lon in locations:
        center += np.array([lat, lon], dtype=float)

    center /= len(locations)
    center = list(center)

    m = ipyleaflet.Map(
        basemap=ipyleaflet.basemap_to_tiles(
            ipyleaflet.basemaps.OpenStreetMap.Mapnik),
        center=center,
        zoom=zoom
    )

    markers = []
    for title, lat, lon in locations:
        mk = ipyleaflet.Marker(draggable=False, title=title,
                               location=(lat, lon))
#         msg = ipywidgets.HTML()
#         msg.value = title
#         msg.placeholder = "Test"
#         msg.description = "Test"
#         mk.popup = msg
        markers.append(mk)

    marker_cluster = ipyleaflet.MarkerCluster(markers=markers)
    m.add(marker_cluster)
    display(m)


def display_locations(locations=[], google_key_api=None, zoom=5):

    if google_key_api is not None:
        geodecode = googlemaps.Client(
            key=google_key_api)
    else:
        geodecode = Nominatim()

    results = []
    for _l in locations:
        if google_key_api is not None:
            res = geodecode.geocode(_l)
            if len(res) == 0:
                print(f"cannot find: {_l}")
                continue
            res = res[0]
            loc = res['geometry']['location']
            results.append((_l, loc['lat'], loc['lng']))
        else:
            res = geodecode.query(_l).toJSON()
            if len(res) == 0:
                print(f"cannot find: {_l}")
                continue
            res = res[0]
            results.append((res['name'], res['lat'], res['lon']))

    display_map(locations=results, zoom=zoom)


################################################################
from IPython.core.interactiveshell import InteractiveShell

def registerFormatter(_type, _format, formatter_functor):
    f = InteractiveShell.instance().display_formatter.formatters[_format]
    f.for_type(_type, func=formatter_functor)

################################################################


def init_printing():
    sympy.init_printing()
    registerFormatter(IPython.core.display.Math,
                      'image/svg+xml', _print_latex_svg)
    registerFormatter(IPython.core.display.Math, 'image/png', _print_latex_png)

################################################################
init_printing()
