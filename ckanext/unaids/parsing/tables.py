from schema import Schema
from pjnz import PJNZFile
import pandas as pd
import numpy as np
from collections import OrderedDict


class ANCPrevalenceSchemedTable(Schema):

    def _extract_anc_ss(self, dataframes):
        dataframes[4].iloc[0, 1] = dataframes[7].iloc[0, 1] = "Region"
        dataframes[5].columns = self._correct_types(dataframes[4].iloc[0])
        dataframes[8].columns = self._correct_types(dataframes[7].iloc[0])
        dataframes[5]['Urban/Rural'] = 'Urban'
        dataframes[8]['Urban/Rural'] = 'Rural'

        anc_ss = pd.concat([dataframes[5], dataframes[8]], sort=False)
        anc_ss.index = range(0, len(anc_ss.index))  # Reset index numbers
        anc_ss.name = dataframes[2].iloc[0, 0][:-5]
        anc_ss = anc_ss.loc[:, anc_ss.columns.notnull()]  # Drop NaN columns
        anc_ss['Site'] = "Aggregated Data"
        anc_ss['Region'] = anc_ss['Region'].map(
            lambda s: s.split(" (%)  (% HIV+)")[0]
        )

        anc_ss['Type'] = 'ANC-SS (%)'
        for index, row in anc_ss.iterrows():
            if index % 2:
                row['Type'] = 'ANC-SS (N)'
                row['Region'] = anc_ss.loc[(index-1)]['Region']
                anc_ss.iloc[index] = row

        return anc_ss

    def _extract_anc_rt(self, dataframes):
        dataframes[26].iloc[0, 1] = dataframes[29].iloc[0, 1] = "Region"
        dataframes[27].columns = self._correct_types(dataframes[26].iloc[0])
        dataframes[30].columns = self._correct_types(dataframes[29].iloc[0])
        dataframes[27]['Urban/Rural'] = 'Urban'
        dataframes[30]['Urban/Rural'] = 'Rural'

        anc_rt = pd.concat([dataframes[27], dataframes[30]], sort=False)
        anc_rt.index = range(0, len(anc_rt.index))  # Reset index numbers
        anc_rt.name = dataframes[2].iloc[0, 0][:-5]
        anc_rt = anc_rt.loc[:, anc_rt.columns.notnull()]  # Drop NaN columns
        anc_rt['Site'] = "Aggregated Data"
        anc_rt['Region'] = anc_rt['Region'].map(
            lambda s: s.split(" (%)  (% HIV+)")[0]
        )

        anc_rt['Type'] = 'ANC-RT (%)'
        for index, row in anc_rt.iterrows():
            if index % 2:
                row['Type'] = 'ANC-RT (N)'
                row['Region'] = anc_rt.loc[(index-1)]['Region']
                anc_rt.iloc[index] = row

        return anc_rt

    def _correct_types(self, array):
        """
        For some reason pandas imports 2005 as a string "2005.0".  This is a
        function to hack a fix.
        """
        for i, v in enumerate(list(array)):
            try:
                array[i] = str(int(v))
            except ValueError:
                pass
        return array

    def create_table(self, spectrum_file):
        """
        Creates a table from the schema and populates it with data from a
        Spectrum File.
        """
        # Load the data and the template
        dataframes = spectrum_file.extract_surv_data()
        template = self.create_template()

        # Extract the required data
        anc_ss = self._extract_anc_ss(dataframes)
        anc_rt = self._extract_anc_rt(dataframes)
        anc = pd.concat([anc_ss, anc_rt], sort=False)

        # Build the table using the template structure
        data = OrderedDict()
        for c in template.columns:
            if c in anc:
                data[c] = list(anc[c])
            else:
                data[c] = [np.NaN]*len(anc.index)
        table = pd.DataFrame.from_dict(data, orient='columns')

        return table


class PMTCTSchemedTable(Schema):

    def create_table(self, spectrum_file):
        """
        Creates a table from the schema and populates it with data from a
        Spectrum File.
        """
        # Load the data and the template.
        data = spectrum_file.extract_dp_table("ARVRegimen MV2")
        template = self.create_template()

        # Drop empty columns at end of data, and assign column names to the data
        key_columns = ['category', 'indicator', 'type']
        headers = key_columns + spectrum_file.year_range
        data = data.drop(range(
            len(headers)+1,
            len(data.columns)+1
        ), axis='columns')
        data.columns = headers

        # Assign row indicies to the data
        PJNZFile.dp_combined_key(data, key_columns)
        data = data.drop(key_columns, axis='columns')

        # Drop the years that we are not interested in from the data
        years_to_drop = map(lambda x: str(x), range(1970, 2000))
        data = data.drop(years_to_drop, axis='columns')

        # Set the first row of the template as the headers
        template.columns = template.iloc[0]
        template = template.iloc[1:]

        # Remove the first schema field as this is the header
        schema = self.schema.copy()
        schema['fields'].pop(0)

        # For other fields map data into template
        for field in schema['fields']:
            if field.get('spectrum_file_key', False):
                # Fill row in with spectrum data (removing the CombinedKey)
                row = data.loc[field['spectrum_file_key']].to_dict()
                template.loc[field['name']] = row
            else:
                # If no spectrum_file_key given, then leave row empty
                template.loc[field['name']] = np.NaN

        template['Indicator'] = template.index

        # We have created returned table by filling in the template.
        return template
