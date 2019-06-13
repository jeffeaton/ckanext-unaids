import json
import pandas as pd
from collections import OrderedDict


class Schema:

    def __init__(self, fpath):
        self.fname = fpath.split('/')[-1][:-5]  # fName w/o path or extension
        with open(fpath, "r") as read_file:
            self.schema = json.load(read_file)

    def create_template(self):
        """
        Creates a template dataframe from the JSON schema.
        """
        # Create the sample data - specifies conditions if no sample data given
        data = OrderedDict()
        for f in self.schema['fields']:
            default_values = ["", "conditions...", "type: "+str(f['type'])]
            for k, v in f.get('constraints', {}).iteritems():
                default_values += [str(k)+": "+str(v)]
            data[f['name']] = [f['name']]+map(str, f.get(
                'example_values',
                default_values
            ))
        template = pd.DataFrame.from_dict(data, orient='index').transpose()

        # Transpose the data if the schema says so
        if self.schema.get('transpose'):
            template = template.transpose()

        return template

    def create_csv_template(self, fname=None):
        """
        Creates a csv template from the GoodTables schema.
        """
        if fname is None:
            fname = self.fname + "_template.csv"
        template = self.create_template()
        file = open(fname, "w")
        file.write(template.to_csv(header=False, index=False))
        file.close()

    def create_table(self, spectrum_file):
        """
        This function should be overriden by sub-classes. It should create
        a table from the schema and populate it with data from a Spectrum File.
        """
        return self.create_template()

    def create_csv_table(self, spectrum_file, fname=None):
        """
        Creates a csv template from the GoodTables schema.
        """
        if fname is None:
            fname = self.fname + "_" + spectrum_file.country + ".csv"
        table = self.create_table(spectrum_file)
        file = open(fname, "w")
        file.write(table.to_csv(header=True, index=False))
        file.close()
