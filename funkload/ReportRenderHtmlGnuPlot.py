# (C) Copyright 2008 Nuxeo SAS <http://nuxeo.com>
# Author: bdelbosc@nuxeo.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
"""Render chart using gnuplot >= 4.2

$Id$
"""

import os
from commands import getstatusoutput
from ReportRenderRst import rst_title
from ReportRenderHtmlBase import RenderHtmlBase
from datetime import datetime


def gnuplot(script_path):
    """Execute a gnuplot script."""
    cmd = 'gnuplot ' + script_path
    ret, output = getstatusoutput(cmd)
    if ret != 0:
        raise RuntimeError("Failed to run gnuplot cmd: " + cmd +
                           "\n" + str(output))

class RenderHtmlGnuPlot(RenderHtmlBase):
    """Render stats in html using gnuplot

    Simply render stuff in ReST than ask docutils to build an html doc.
    """
    # for testing TODO: remove
    chart_size = (640, 480)

    color_success = 0x00ff00
    color_error = 0xff0000
    color_time = 0x0000ff
    color_time_min_max = 0xccccee
    color_grid = 0xcccccc
    color_line = 0x333333
    color_plot = 0x003a6b
    color_bg = 0xffffff
    color_line = 0x000000


    def getChartSizeTmp(self, cvus):
        """Override for gnuplot format"""
        size = RenderHtmlBase.getChartSize(self, cvus)
        return str(size[0]) + ',' + str(size[1])


    def createTestChart(self):
        """Create the test chart."""
        image_path = str(os.path.join(self.report_dir, 'tests.png'))
        gplot_path = str(os.path.join(self.report_dir, 'tests.gplot'))
        data_path = str(os.path.join(self.report_dir, 'tests.data'))
        stats = self.stats
        # data
        lines = ["CUs STPS ERROR"]
        cvus = []
        for cycle in self.cycles:
            if not stats[cycle].has_key('test'):
                continue
            values = []
            test = stats[cycle]['test']
            values.append(str(test.cvus))
            cvus.append(str(test.cvus))
            values.append(str(test.tps))
            error = test.error_percent
            values.append(str(error))
            lines.append(' '.join(values))
        f = open(data_path, 'w')
        f.write('\n'.join(lines) + '\n')
        f.close()
        # script
        lines = ['set output "' + image_path +'"']
        lines.append('set title "Successful Tests Per Second"')
        lines.append('set xlabel "Concurrent Users"')
        lines.append('set ylabel "Tests Per Second"')
        lines.append('set grid')
        lines.append('set terminal png size ' + self.getChartSizeTmp(cvus))

        lines.append('plot "%s" u 1:3 w boxes lw 2 t "Errors", '
                     '"" u 1:2 w linespoints lw 2 t "STTPS"' % data_path)
        f = open(gplot_path, 'w')
        f.write('\n'.join(lines) + '\n')
        f.close()
        gnuplot(gplot_path)


    def appendDelays(self, delay, delay_low, delay_high, stats):
        """ Show percentiles or min, avg and max in chart. """
        if self.options.with_percentiles:
            delay.append(stats.percentiles.perc50)
            delay_low.append(stats.percentiles.perc10)
            delay_high.append(stats.percentiles.perc90)
        else:
            delay.append(stats.avg)
            delay_low.append(stats.min)
            delay_high.append(stats.max)


    def createPageChart(self):
        """Create the page chart."""
        image_path = str(os.path.join(self.report_dir, 'pages_spps.png'))
        image2_path = str(os.path.join(self.report_dir, 'pages.png'))
        gplot_path = str(os.path.join(self.report_dir, 'pages.gplot'))
        data_path = str(os.path.join(self.report_dir, 'pages.data'))
        stats = self.stats
        # data
        lines = ["CUs SPPS ERROR MIN AVG MAX P10 P50 P90 P95"]
        cvus = []
        for cycle in self.cycles:
            if not stats[cycle].has_key('page'):
                continue
            values = []
            page = stats[cycle]['page']
            values.append(str(page.cvus))
            cvus.append(str(page.cvus))
            values.append(str(page.rps))
            error = page.error_percent
            values.append(str(error))
            values.append(str(page.min))
            values.append(str(page.avg))
            values.append(str(page.max))
            values.append(str(page.percentiles.perc10))
            values.append(str(page.percentiles.perc50))
            values.append(str(page.percentiles.perc90))
            values.append(str(page.percentiles.perc95))
            lines.append(' '.join(values))
        f = open(data_path, 'w')
        f.write('\n'.join(lines) + '\n')
        f.close()
        # script
        lines = ['set output "' + image_path +'"']
        lines.append('set title "Successful Pages Per Second"')
        lines.append('set xlabel "Concurrent Users"')
        lines.append('set ylabel "Pages Per Second"')
        lines.append('set grid')
        lines.append('set terminal png size ' + self.getChartSizeTmp(cvus))
        lines.append('plot "%s" u 1:3 w boxes lw 2 t "Errors", '
                     '"" u 1:2 w linespoints lw 2 t "STTPS"' % data_path)

        lines.append('set output "%s"' % image2_path)
        lines.append('set title "Pages Response time"')
        lines.append('set ylabel "Duration (s)"')
        lines.append('set bars 5.0')
        lines.append('set grid back')
        lines.append('set style fill solid .25')
        lines.append('plot "%s" u 1:8:8:10:9 t "med/p90/p95" w candlesticks lt 1 lw 1 whiskerbars 0.5, "" u 1:7:4:8:8 w candlesticks lt 2 lw 1 t "min/p10/med" whiskerbars 0.5, "" u 1:5 t "avg" w lines lt 3 lw 2' % data_path)
        f = open(gplot_path, 'w')
        f.write('\n'.join(lines) + '\n')
        f.close()
        gnuplot(gplot_path)



    def createAllResponseChart(self):
        """Create global responses chart."""
        image_path = str(os.path.join(self.report_dir, 'requests_rps.png'))
        image2_path = str(os.path.join(self.report_dir, 'requests.png'))
        gplot_path = str(os.path.join(self.report_dir, 'requests.gplot'))
        data_path = str(os.path.join(self.report_dir, 'requests.data'))
        stats = self.stats
        # data
        lines = ["CUs RPS ERROR MIN AVG MAX P10 P50 P90 P95"]
        cvus = []
        for cycle in self.cycles:
            if not stats[cycle].has_key('response'):
                continue
            values = []
            resp = stats[cycle]['response']
            values.append(str(resp.cvus))
            cvus.append(str(resp.cvus))
            values.append(str(resp.rps))
            error = resp.error_percent
            values.append(str(error))
            values.append(str(resp.min))
            values.append(str(resp.avg))
            values.append(str(resp.max))
            values.append(str(resp.percentiles.perc10))
            values.append(str(resp.percentiles.perc50))
            values.append(str(resp.percentiles.perc90))
            values.append(str(resp.percentiles.perc95))
            lines.append(' '.join(values))
        f = open(data_path, 'w')
        f.write('\n'.join(lines) + '\n')
        f.close()
        # script
        lines = ['set output "' + image_path +'"']
        lines.append('set title "Requests Per Second"')
        lines.append('set xlabel "Concurrent Users"')
        lines.append('set ylabel "Requests Per Second"')
        lines.append('set grid')
        lines.append('set terminal png size ' + self.getChartSizeTmp(cvus))
        lines.append('plot "%s" u 1:3 w boxes lw 2 t "Errors", '
                     '"" u 1:2 w linespoints lw 2 t "STTPS"' % data_path)

        lines.append('set output "%s"' % image2_path)
        lines.append('set title "Requests Response time"')
        lines.append('set ylabel "Duration (s)"')
        lines.append('set bars 5.0')
        lines.append('set grid back')
        lines.append('set style fill solid .25')
        lines.append('plot "%s" u 1:8:8:10:9 t "med/p90/p95" w candlesticks lt 1 lw 1 whiskerbars 0.5, "" u 1:7:4:8:8 w candlesticks lt 2 lw 1 t "min/p10/med" whiskerbars 0.5, "" u 1:5 t "avg" w lines lt 3 lw 2' % data_path)
        f = open(gplot_path, 'w')
        f.write('\n'.join(lines) + '\n')
        f.close()
        gnuplot(gplot_path)

        return


    def createResponseChart(self, step):
        """Create responses chart."""
        image_path = str(os.path.join(self.report_dir,
                                      'request_%s.png' % step))
        gplot_path = str(os.path.join(self.report_dir, 'request_%s.gplot' % step))
        data_path = str(os.path.join(self.report_dir, 'request_%s.data' % step))
        stats = self.stats
        # data
        lines = ["CUs STEP ERROR MIN AVG MAX P10 P50 P90 P95"]
        cvus = []
        for cycle in self.cycles:
            if not stats[cycle]['response_step'].has_key(step):
                continue
            values = []
            resp = stats[cycle]['response_step'].get(step)
            values.append(str(resp.cvus))
            cvus.append(str(resp.cvus))
            values.append(str(step))
            error = resp.error_percent
            values.append(str(error))
            values.append(str(resp.min))
            values.append(str(resp.avg))
            values.append(str(resp.max))
            values.append(str(resp.percentiles.perc10))
            values.append(str(resp.percentiles.perc50))
            values.append(str(resp.percentiles.perc90))
            values.append(str(resp.percentiles.perc95))
            lines.append(' '.join(values))
        f = open(data_path, 'w')
        f.write('\n'.join(lines) + '\n')
        f.close()
        # script
        lines = []
        lines.append('set output "%s"' % image_path)
        lines.append('set terminal png size ' + self.getChartSizeTmp(cvus))
        lines.append('set grid')
        lines.append('set bars 5.0')
        lines.append('set title "Request %s Response time"' % step)
        lines.append('set xlabel "Concurrent Users"')
        lines.append('set ylabel "Duration (s)"')
        lines.append('set grid back')
        lines.append('set style fill solid .25')
        lines.append('plot "%s" u 1:8:8:10:9 t "med/p90/p95" w candlesticks lt 1 lw 1 whiskerbars 0.5, "" u 1:7:4:8:8 w candlesticks lt 2 lw 1 t "min/p10/med" whiskerbars 0.5, "" u 1:5 t "avg" w lines lt 3 lw 2' % data_path)
        f = open(gplot_path, 'w')
        f.write('\n'.join(lines) + '\n')
        f.close()
        gnuplot(gplot_path)

        return


    # monitoring charts
    def createMonitorCharts(self):
        """Create all montirored server charts."""
        if not self.monitor or not self.with_chart:
            return
        self.append(rst_title("Monitored hosts", 2))
        for host in self.monitor.keys():
            self.createMonitorChart(host)


    def createMonitorChart(self, host):
        """Create monitrored server charts."""
        stats = self.monitor[host]
        time_start = float(stats[0].time)
        times = []
        cvus_list = []
        for stat in stats:
            test, cycle, cvus = stat.key.split(':')
            date = datetime.fromtimestamp(float(stat.time))
            times.append(date.strftime("%H:%M:%S"))
            #times.append(int(float(stat.time))) # - time_start))
            cvus_list.append(cvus)

        mem_total = int(stats[0].memTotal)
        mem_used = [mem_total - int(x.memFree) for x in stats]
        mem_used_start = mem_used[0]
        mem_used = [x - mem_used_start for x in mem_used]

        swap_total = int(stats[0].swapTotal)
        swap_used = [swap_total - int(x.swapFree) for x in stats]
        swap_used_start = swap_used[0]
        swap_used = [x - swap_used_start for x in swap_used]

        load_avg_1 = [float(x.loadAvg1min) for x in stats]
        load_avg_5 = [float(x.loadAvg5min) for x in stats]
        load_avg_15 = [float(x.loadAvg15min) for x in stats]

        net_in = [None]
        net_out = [None]
        cpu_usage = [0]
        for i in range(1, len(stats)):
            if not (hasattr(stats[i], 'CPUTotalJiffies') and
                    hasattr(stats[i-1], 'CPUTotalJiffies')):
                cpu_usage.append(None)
            else:
                dt = ((long(stats[i].IDLTotalJiffies) +
                       long(stats[i].CPUTotalJiffies)) -
                      (long(stats[i-1].IDLTotalJiffies) +
                       long(stats[i-1].CPUTotalJiffies)))
                if dt:
                    ttl = (float(long(stats[i].CPUTotalJiffies) -
                                 long(stats[i-1].CPUTotalJiffies)) /
                           dt)
                else:
                    ttl = None
                cpu_usage.append(ttl)
            if not (hasattr(stats[i], 'receiveBytes') and
                    hasattr(stats[i-1], 'receiveBytes')):
                net_in.append(None)
            else:
                net_in.append((int(stats[i].receiveBytes) -
                               int(stats[i-1].receiveBytes)) /
                              (1024 * (float(stats[i].time) -
                                       float(stats[i-1].time))))

            if not (hasattr(stats[i], 'transmitBytes') and
                    hasattr(stats[i-1], 'transmitBytes')):
                net_out.append(None)
            else:
                net_out.append((int(stats[i].transmitBytes) -
                                int(stats[i-1].transmitBytes))/
                              (1024 * (float(stats[i].time) -
                                       float(stats[i-1].time))))

        image_path = str(os.path.join(self.report_dir, '%s_load.png' % host))
        data_path = str(os.path.join(self.report_dir, '%s_load.data' % host))
        gplot_path = str(os.path.join(self.report_dir, '%s_load.gplot' % host))

        data = [times, cvus_list, cpu_usage, load_avg_1, load_avg_5, load_avg_15,
                mem_used, swap_used, net_in, net_out ]
        data = zip(*data)
        f = open(data_path, 'w')
        f.write("TIME CUs CPU LOAD1 LOAD5 LOAD15 MEM SWAP NETIN NETOUT\n")
        for line in data:
            f.write(' '.join([str(item) for item in line]) + '\n')
        f.close()

        lines = []
        lines.append('set output "%s"' % image_path)
        lines.append('set terminal png size ' + self.getChartSizeTmp(cvus))
        lines.append('set grid')
        lines.append('set title "%s Load' % host)
        lines.append('set ylabel "Load"')
        lines.append('set xdata time')
        lines.append('set timefmt "%H:%M:%S"')
        lines.append('set grid back')
        lines.append('set multiplot')
        lines.append('set size 1, 0.7')
        lines.append('set origin 0, 0.3')
        lines.append('set bmargin 0')
        lines.append('set lmargin 9')
        lines.append('set rmargin 2')
        lines.append('set format x ""')
        lines.append('set style fill solid .25')
        lines.append('plot "%s" u 1:3 t "CPU 1=100%%" w impulse lw 2 lt 1, "" u 1:4 t "Load 1min" w lines lw 2 lt 3, "" u 1:5 t "Load 5min" w lines lw 2 lt 4, "" u 1:6 t "Load 15min" w lines lw 2 lt 5' % data_path)
        lines.append('set ylabel "CUS"')
        lines.append('set bmargin')
        lines.append('set format x "%H:%M"')
        lines.append('unset title')
        lines.append('unset grid')
        lines.append('set autoscale y')
        lines.append('set style fill solid .25')
        lines.append('set size 1.0, 0.3')
        lines.append('set ytics 10')
        lines.append('set xlabel "Time"')
        lines.append('set origin 0.0, 0.0')
        lines.append('plot "%s" u 1:2 notitle with impulse lw 2 lt 3' % data_path)
        lines.append('unset multiplot')
        f = open(gplot_path, 'w')
        f.write('\n'.join(lines) + '\n')
        f.close()
        gnuplot(gplot_path)

        # TODO: add mem and net charts !
        return


