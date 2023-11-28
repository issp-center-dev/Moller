import ruamel.yaml as yaml
import csv
from tabulate import tabulate

class TaskStatus:
    def __init__(self, info_file, list_file=None, flt=None):
        self.setup(info_file, list_file, self._make_filter(flt))

    def _make_filter(self, flt):
        if flt is None:
            return lambda vv: True
        elif flt == "ok":
            return lambda vv: all([v == 'o' for v in vv])
        elif flt == "failed":
            return lambda vv: any([v != 'o' for v in vv])
        elif flt == "collapsed":
            return lambda vv: any([v == 'x' for v in vv])
        elif flt == "skipped":
            return lambda vv: any([v == '-' for v in vv])
        elif flt == "yet":
            return lambda vv: any([v == '.' for v in vv])
        elif flt == "debug":
            return lambda vv: False
        else: # "all" and others
            return lambda vv: True

    def setup(self, info_file, list_file, flt):
        taskitems = self.read_script(info_file)

        task_data = []
        for task_name, log_file in taskitems:
            task_data.append((task_name, self.read_joblog(log_file)))

        if list_file is None:
            # gather from joblog entries
            z = set()
            for i,v in task_data:
                z |= set(v.keys())
            jobitems = sorted(list(z))
        else:
            jobitems = self.read_listfile(list_file)

        tbl = []
        tbl.append(['job'] + [ task_name for task_name, job_log in task_data ])

        for jobitem in jobitems:
            d = []
            for task_name, job_log in task_data:
                if jobitem in job_log:
                    x = job_log[jobitem][-1]
                    if 'Exitval' in x:
                        stat = int(x['Exitval'])
                        if stat == 0:
                            d.append('o')
                        elif stat == 255:
                            d.append('-')
                        else:
                            d.append('x')
                    else:
                        d.append('#')
                else:
                    d.append('.')

            if flt(d):
                tbl.append([jobitem] + d)

        self.status_table = tbl

    def read_joblog(self, logfile):
        import os
        if os.path.isfile(logfile):
            return self.read_joblog_file(logfile)
        else:
            import glob
            logfiles = glob.glob(f"{logfile}.*")
            if len(logfiles) == 0:
                return {}
            else:
                return self.read_joblog_set(logfiles)

    def read_joblog_file(self, logfile):
        task_table = {}
        try:
            with open(logfile, 'r') as fp:
                lines = [ s.strip() for s in fp.readlines() ]
        except Exception as e:
            raise RuntimeError(e)

        itemkeys = lines[0].split('\t')
        for line in lines[1:]:
            items = line.split('\t')
            tbl = { a: b for a,b in zip(itemkeys, items) }

            cmditems = tbl['Command'].split()
            if len(cmditems) == 4:
                # single parallel
                task_name, signature, work_item, slot_id = cmditems
            elif len(cmditems) == 7:
                # nested parallel
                dummy1, task_name, signature, work_item, a, b, c = cmditems
                slot_id = (int(a) - 1) * int(b) + int(c)
            else:
                raise RuntimeError("unknown format in Command field")

            tbl.update({'task_name': task_name, 'signature': signature, 'work_item': work_item, 'slot_id': slot_id})
            if work_item in task_table:
                task_table[work_item].append(tbl)
            else:
                task_table[work_item] = [tbl]
        return task_table

    def read_joblog_set(self, logfiles):
        task_table = {}
        for logfile in logfiles:
            task_table.update(self.read_joblog_file(logfile))
        return task_table

    def read_script(self, scriptfile):
        try:
            with open(scriptfile, 'r') as fp:
                info_dict = yaml.safe_load(fp)
        except yaml.YAMLError as e:
            raise RuntimeError('yaml error: {}'.format(e))
        except Exception as e:
            raise RuntimeError(e)

        task_list = []
        for task_name, task_info in info_dict.get('jobs', {}).items():
            task_type = task_info.get('parallel', True)
            if task_type:
                log_file = "log_{}.dat".format(task_name)
                task_list.append((task_name, log_file))

        return task_list

    def read_listfile(self, listfile):
        try:
            with open(listfile, 'r') as fp:
                lines = [ s.strip() for s in fp.readlines() ]
        except Exception as e:
            raise RuntimeError(e)

        return lines

    def write(self, mode, output_file):
        if mode is None or mode == "text":
            self.write_table(output_file)
        elif mode == "csv":
            self.write_csv(output_file)
        elif mode == "html":
            self.write_html(output_file)
        else:
            raise RuntimeError("unknown format: {}".format(mode))

    def write_table(self, output_file):
        tbl = self.status_table
        if output_file is None:
            print(tabulate(tbl[1:], headers=tbl[0], tablefmt='github'))
        else:
            with open(output_file, "w") as fp:
                fp.write(tabulate(tbl[1:], headers=tbl[0], tablefmt='github'))

    def write_csv(self, output_file):
        if output_file is None:
            import sys
            writer = csv.writer(sys.stdout)
            writer.writerows(self.status_table)
        else:
            with open(output_file, "w") as fp:
                writer = csv.writer(fp)
                writer.writerows(self.status_table)

    def write_html(self, output_file):
        mark = { 'o': '&#10004;', 'x': '&#10060;', '-': '&#8212;', '.': '.', '#': '#' }

        str = r"""
<html>
  <head>
    <title>Status: sample</title>
    <style type="text/css">
      <!--
      .design13 {
          font-family: sans-serif;
          width: 100%;
          text-align: center;
          border-collapse: collapse;
          border-spacing: 0;
          background: #778ca3;
          color: #ffffff;
      }
      .design13 th {
          width: 100px;
          padding: 10px;
          background: #4b6584;
          border: solid 1px #ffffff;
      }
      .design13 th:first-child {
          width: 150px;
      }
      .design13 td {
          padding: 10px;
          border: solid 1px #ffffff;
      }
      .design13 td:first-child {
          padding: 10px;
          background: #4b6584;
      }
      //-->
    </style>
  </head>
  <body>
    <table class="design13">
"""

        str += "<tr>\n"
        for item in self.status_table[0]:
            str += "  <th>{}</th>\n".format(item)
        str += "</tr>\n"
        for items in self.status_table[1:]:
            str += "<tr>\n"
            str += "  <td>{}</td>\n".format(items[0])
            for item in items[1:]:
                str += "  <td>{}</td>\n".format(mark[item])
            str += "</tr>\n"
            
        str += r"""
    </table>
  </body>
</html>
"""
        if output_file is None:
            print(str)
        else:
            with open(output_file, "w") as fp:
                fp.write(str)
        
def main():
    import argparse

    parser = argparse.ArgumentParser(prog='moller_status')
    parser.add_argument('input_yaml', default=None, help='task description file (input.yaml)')
    parser.add_argument('job_list', nargs='?', default=None, help='job list file (list.dat)')
    parser.add_argument('-o', '--output', dest='output_file', metavar='output_file', default=None, help='output file')
    parse_target = parser.add_mutually_exclusive_group()
    parse_target.add_argument('--text', action='store_const', const='text', dest='mode', help='output in text format')
    parse_target.add_argument('--csv',  action='store_const', const='csv',  dest='mode', help='output in csv format')
    parse_target.add_argument('--html', action='store_const', const='html', dest='mode', help='output in html format')
    parse_filter = parser.add_mutually_exclusive_group()
    parse_filter.add_argument('--ok', action='store_const', const='ok', dest='filt', help='show successful jobs')
    parse_filter.add_argument('--failed', action='store_const', const='failed', dest='filt', help='show failed jobs')
    parse_filter.add_argument('--skipped', action='store_const', const='skipped', dest='filt', help='show skipped jobs')
    parse_filter.add_argument('--yet', action='store_const', const='yet', dest='filt', help='show jobs not yet started')
    parse_filter.add_argument('--collapsed', action='store_const', const='collapsed', dest='filt', help='show failed tasks')
    parse_filter.add_argument('--all', action='store_const', const='all', dest='filt', help='show all jobs')
    parse_filter.add_argument('--debug', action='store_const', const='debug', dest='filt', help=argparse.SUPPRESS) # show no jobs

    args = parser.parse_args()

    status = TaskStatus(args.input_yaml, args.job_list, args.filt)
    status.write(args.mode, args.output_file)

if __name__ == '__main__':
    main()
