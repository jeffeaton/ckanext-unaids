import zipfile
import pandas as pd
import numpy as np


class PJNZFile():

    # Determining the files in the PJNZ that we want to import to Pandas
    # Key is the suffix, Value specifies kwargs sent to read_csv
    file_suffixes = {
        '_surv.csv': {},
        '.ep1': {},
        '.ep3': {},
        '.ep4': {},
        '.ep5': {},
        '.DP': {'dtype': str}
    }
    year_range = map(lambda x: str(x), range(1970, 2026))

    def __init__(self, fpath, file_suffixes=file_suffixes, country=None):
        """
        Files are extracted upon object creation.
        """
        self.fpath = fpath
        self.fname = fpath.split('/')[-1][:-5]  # fName w/o path or extension
        self.file_suffixes = file_suffixes
        self.pjnz_file = zipfile.PyZipFile(fpath)
        if country:
            self.country = country
        else:
            self.country = fpath.split('/')[-1].split('_')[0]

        self.extract_files()

    @staticmethod
    def _add_delimiters(file_object, delimiter=','):
        """
        Pandas does not allow the import of irregular shaped CSV files - the first row must have
        more elements that any other row.  This function adds extra delimiters to the first row so
        it matches the longest row in length.  All empty cells will be assigned NaN if the Pandas
        dataframe.
        """
        s_data = ''
        max_num_delimiters = 0

        with file_object as f:
            for line in f:
                s_data += line
                delimiter_count = line.count(delimiter)
                if delimiter_count > max_num_delimiters:
                    max_num_delimiters = delimiter_count

        s_delimiters = delimiter * max_num_delimiters + '\n'

        return io.StringIO(unicode(s_delimiters + s_data, "utf-8"))

    def extract_files(self):
        """
        This funtion takes each of the specified file_suffixes and try's to
        import it as a Pandas dataframe, using the specified kwargs.
        """
        self.dataframes = {}
        for file_suffix, kwargs in self.file_suffixes.items():
            filename = self.fname + file_suffix
            self.dataframes[filename] = pd.read_csv(
                PJNZFile._add_delimiters(
                    self.pjnz_file.open(filename, 'r')
                ),
                **kwargs
            )

    def extract_dp_table(self, tag):
        """
        The DP file appears to be made up of a number of subsidary dataframes,
        each taggedv and labelled. There isn't a clear pattern to the way
        they are structured in the sheet, but this function broadly pulls
        out a subset of the DP sheet for a given tag.
        """
        # Get the entire DP sheet with rows and columns indexed by numbers
        dp_sheet = self.dataframes.get(self.fname + '.DP')
        if dp_sheet is None:
            raise FileNotFoundError("DP sheet not found")
        dp_sheet.columns = range(0, len(dp_sheet.columns))

        # Find desired tag in first column
        tag = "<" + str(tag) + ">"
        start_row = dp_sheet.index[dp_sheet[0] == tag].tolist()[0]

        # Find end tag that follows the desired tag
        tag = "<End>"
        end_rows = dp_sheet.index[dp_sheet[0] == tag].tolist()
        for n in end_rows:
            if n > start_row:
                end_row = n
                break

        # Slice out the desired sub-table, and store the table name and tag.
        dp_table = dp_sheet.copy().iloc[start_row+2:end_row, 1:]
        dp_table.iloc[0, 0] = np.NaN  # remove the <value> tag
        dp_table.name = dp_sheet.iloc[start_row+1, 1]
        dp_table.tag = tag
        return dp_table

    def extract_surv_data(self):
        """
        The ANC Sentinel Surveillance and Routine Testing data are stored in
        the surv file.  This breaks the surv data down in to sub dataframes
        using the =========== and ---------- dividers.
        """
        # Get entire surv.csv sheet with rows and columns indexed by numbers
        surv_sheet = self.dataframes.get(self.fname + '_surv.csv')
        if surv_sheet is None:
            raise FileNotFoundError("surv.csv sheet not found")
        surv_sheet.columns = range(0, len(surv_sheet.columns))

        # Divide up the data into multiple smaller data frames
        tags = "=============================|------------------------------"
        dividing_rows = surv_sheet.index[
            surv_sheet[0].str.contains(tags, na=False, regex=True)
        ].tolist()
        dataframes = []
        for index, row in enumerate(dividing_rows):
            start_row = row+1
            try:
                end_row = dividing_rows[index+1]
            except IndexError:
                break
            table = surv_sheet.copy().iloc[start_row:end_row, 0:]
            dataframes.append(table)

        return dataframes

    @staticmethod
    def dp_combined_key(dataframe, columns, sep=" - "):
        """
        Combines multiple columns of a DP dataset into a single combined key.
        """
        dataframe['CombinedKey'] = ""
        old_keys = ['', '', '']
        for index, row in dataframe.iterrows():
            # Load the new set of keys
            keys = map(lambda c: str(row[c]), columns)
            # Override empty key fields with the previous rows value
            # This is just the way data is structured in the file
            for i, key in enumerate(keys):
                if key in ['', None, 'nan']:
                    keys[i] = old_keys[i]
            old_keys = keys
            # Create new key
            row['CombinedKey'] = sep.join(filter(None, keys))

        dataframe.index = dataframe['CombinedKey']
        del dataframe['CombinedKey']
