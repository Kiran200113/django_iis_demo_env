from django.shortcuts import render, HttpResponse
# from openpyxl import load_workbook
import pandas as pd
from django.views import View
from django.core.cache import cache
from django.contrib import messages

context = { 
        "data" : [
            ['Statistics', 'Row Required', 'Row Required', 'Row Required', 'Value Required'], 
            ['RSF1', 'Text Required', 'Decimal Required', 'Not Required', 'Not Required'], 
            ['RSF2', 'Text Required', 'Decimal Required', 'Not Required', 'Not Required'], 
            ['RSF3', 'Text Required', 'Decimal Required', 'Not Required', 'Not Required'], 
            ['Round First & Max', 'Decimal Required', 'Text Required', 'Date Required', 'Not Required'], 
            ['SSS1', 'Any Required', 'Any Required', 'Any Required', 'Any Required'], 
            ['SSS2', 'Any Required', 'Any Required', 'Any Required', 'Any Required'], 
            ['SSD-V', 'Any Required', 'Any Required', 'Any Required', 'Any Required'], 
            ['SSR-R', 'Any Required', 'Any Required', 'Any Required', 'Any Required'],
        ]
    } 

# Create your views here.
def index(request):
        
    if request.method == 'POST' and request.FILES['excel_file']:
        excel_file = request.FILES['excel_file']

        # Get the uploaded file name
        uploaded_file_name = excel_file.name

        # Use pandas to read the Excel file
        df = pd.read_excel(excel_file)
       
        column_names = df.columns.tolist()
        context['columns'] = column_names
        context['uploaded_file_name'] = uploaded_file_name

        cache.set('excel_data', df.to_dict())
        return render(request, 'index.html', context)        
    else:
        key_to_remove = 'uploaded_file_name'
        if key_to_remove in context:        
            del context['uploaded_file_name']
            del context['columns']
            cache.delete('excel_data')

        return render(request, 'index.html', context)


def generateExcel(request):
    error_occurred = False  # Flag to track if an error occurred
    data = cache.get('excel_data')
    excel_data = pd.DataFrame.from_dict(data)

    if request.method == 'POST':
        try:
            if excel_data.empty:
                messages.warning(request, f'Please, Upload the excel file!')
                error_occurred = True
            else:
                excel_writer = pd.ExcelWriter('D:/Output.xlsx', engine='xlsxwriter')
                dataframes = {}

                selected_options = {}
                checked_checkboxes = []

                # Process selected options from dropdowns
                for key, value in request.POST.items():          
                    if key.startswith('select_'):                
                        selected_options[key] = value

                # Process checked checkboxes
                for key, value in request.POST.items():
                    if key.startswith('checkbox') and value == 'on':
                        checked_checkboxes.append(key)

                if checked_checkboxes:
                    excel_data.to_excel(excel_writer, sheet_name='Source', index=False) 
                    for item in checked_checkboxes:

                        # If Statistics Checked
                        if item == 'checkbox_Statistics':              
                            group = excel_data.groupby(selected_options['select_1_1'])
                            # sumOfCol = group[selected_options['select_1_2']].sum()
                            # countOfCol = group[selected_options['select_1_2']].count()
                            # avgOfCol = group[selected_options['select_1_2']].mean()
                            # minOfCol = group[selected_options['select_1_2']].min()
                            # maxOfCol = group[selected_options['select_1_2']].max()
                            
                            index_columns = []
                            # Check if user provided select_1_1 option
                            if 'select_1_1' in selected_options:
                                index_columns.append(selected_options['select_1_1'])

                            # Check if user provided select_1_2 option
                            if 'select_1_2' in selected_options:
                                index_columns.append(selected_options['select_1_2'])

                            # Check if user provided select_1_3 option
                            if 'select_1_3' in selected_options:
                                index_columns.append(selected_options['select_1_3'])

                            statistics = pd.pivot_table(excel_data, index=index_columns, values=selected_options['select_1_4'],  aggfunc={selected_options['select_1_4']: ['sum', 'count', 'mean', 'min', 'max']}).unstack()
                            statistics.to_excel(excel_writer, sheet_name='Statistics')                

                        # If RSF1 Checked            
                        if item == 'checkbox_RSF1':
                            group = excel_data.groupby(selected_options['select_2_1'])
                            maxOfCol = group[selected_options['select_2_2']].max()
                            secondMaxOfCol = group[selected_options['select_2_2']].apply(lambda x: x.sort_values(ascending=False).iloc[2])
                            countOfCol = group[selected_options['select_2_2']].count()
                            divisionCol = (maxOfCol / secondMaxOfCol).round(4)

                            rsf1 = pd.concat([maxOfCol, secondMaxOfCol, countOfCol, divisionCol], axis=1, keys=['Largest', 'SecondLargest', 'Count', 'Division'])
                            rsf1.reset_index(inplace=True)
                            rsf1 = pd.merge(rsf1, excel_data[selected_options['select_2_1']], on=selected_options['select_2_1'])

                            rsf1.drop_duplicates(subset=[selected_options['select_2_1']], inplace=True)
                            rsf1.columns = [''.join(col) for col in rsf1.columns]
                            rsf1.to_excel(excel_writer, sheet_name='RSF1', index=False)                

                        # If RSF2 Checked
                        if item == 'checkbox_RSF2':
                            group = excel_data.groupby(selected_options['select_3_1'])
                            maxOfCol = group[selected_options['select_3_2']].max()
                            avgOfCol = group[selected_options['select_3_2']].mean()
                            countOfCol = group[selected_options['select_3_2']].count()
                            divisionCol = (maxOfCol / avgOfCol).round(4)

                            rsf2 = pd.concat([maxOfCol, avgOfCol, countOfCol, divisionCol], axis=1, keys=['Largest', 'Average', 'Count', 'Division'])
                            rsf2.reset_index(inplace=True)
                            rsf2 = pd.merge(rsf2, excel_data[selected_options['select_3_1']], on=selected_options['select_3_1'])

                            rsf2.drop_duplicates(subset=[selected_options['select_3_1']], inplace=True)
                            rsf2.to_excel(excel_writer, sheet_name='RSF2', index=False)                

                        # If RSF3 Checked
                        if item == 'checkbox_RSF3':
                            group = excel_data.groupby(selected_options['select_4_1'])
                            minOfCol = group[selected_options['select_4_2']].min()
                            avgOfCol = group[selected_options['select_4_2']].mean()
                            countOfCol = group[selected_options['select_4_2']].count()
                            divisionCol = (minOfCol / avgOfCol).round(4)

                            rsf3 = pd.concat([minOfCol, avgOfCol, countOfCol, divisionCol], axis=1, keys=['Smallest', 'Average', 'Count', 'Division'])
                            rsf3.reset_index(inplace=True)
                            rsf3 = pd.merge(rsf3, excel_data[selected_options['select_4_1']], on=selected_options['select_4_1'])

                            rsf3.drop_duplicates(subset=[selected_options['select_4_1']], inplace=True)
                            rsf3.to_excel(excel_writer, sheet_name='RSF3', index=False)   

                        # If Round First & Max Checked
                        if item == 'checkbox_Round First & Max':
                            excel_data[selected_options['select_5_1']] = pd.to_numeric(excel_data[selected_options['select_5_1']], errors='coerce')
                            excel_data[selected_options['select_5_3']] = pd.to_datetime(excel_data[selected_options['select_5_3']], errors='coerce')
                            
                            new_dt = excel_data
                            new_dt['Round'] = ""
                            new_dt['First'] = ""
                            new_dt['Max'] = ""

                            dtrsfmin = new_dt.groupby(selected_options['select_5_2']).agg(
                                First=(selected_options['select_5_3'], 'min'),
                                Max=(selected_options['select_5_1'], 'max')
                            ).reset_index()               
                            
                            for index, row in new_dt.iterrows():
                                value = float(row[selected_options['select_5_1']]) if row[selected_options['select_5_1']] != "" else 0
                                name = str(row[selected_options['select_5_2']])
                                date = str(row[selected_options['select_5_3']])

                                if value % 1000 == 0 and value != 0:
                                    new_dt.at[index, 'Round'] = "Round"

                                for _, item1 in dtrsfmin.iterrows():
                                    name_mapped = str(item1[selected_options['select_5_2']])
                                    first = str(item1["First"])
                                    max_val = float(item1["Max"]) if item1["Max"] != "" else 0

                                    if name_mapped == name and first == date:
                                        new_dt.at[index, 'First'] = "First"

                                    if name_mapped == name and max_val == value:
                                        new_dt.at[index, 'Max'] = "Max"

                            new_dt.to_excel(excel_writer, sheet_name='Round First & Max', index=False)

                        # If SSS1 Checked
                        if item == 'checkbox_SSS1':
                            combined = excel_data[selected_options['select_6_1']].astype(str) + '!' + excel_data[selected_options['select_6_2']].astype(str) + '!' + excel_data[selected_options['select_6_3']].astype(str) + '!' + excel_data[selected_options['select_6_4']].astype(str)

                            sss1 = pd.concat([excel_data[selected_options['select_6_1']], excel_data[selected_options['select_6_2']], 
                                excel_data[selected_options['select_6_3']], excel_data[selected_options['select_6_4']], combined], axis=1, 
                                keys=[selected_options['select_6_1'], selected_options['select_6_2'], selected_options['select_6_3'], 
                                selected_options['select_6_4'], 'Combined'])
                            sss1.to_excel(excel_writer, sheet_name='SSS1', index=False)

                        # If SSS2 Checked
                        if item == 'checkbox_SSS2':
                            combined = excel_data[selected_options['select_7_1']].astype(str) + '!' + excel_data[selected_options['select_7_2']].astype(str) + '!' + excel_data[selected_options['select_7_3']].astype(str) + '!' + excel_data[selected_options['select_7_4']].astype(str)

                            sss2 = pd.concat([excel_data[selected_options['select_7_1']], excel_data[selected_options['select_7_2']], 
                                excel_data[selected_options['select_7_3']],  excel_data[selected_options['select_7_4']], combined], axis=1, 
                                keys=[selected_options['select_7_1'], selected_options['select_7_2'], selected_options['select_7_3'], 
                                selected_options['select_7_4'], 'Combined'])   

                            dataframes['SSS2'] = sss2
                            sss2.to_excel(excel_writer, sheet_name='SSS2', index=False)

                        # If SSD-V Checked
                        if item == 'checkbox_SSD-V':
                            combined = excel_data[selected_options['select_8_1']].astype(str) + '!' + excel_data[selected_options['select_8_2']].astype(str) + '!' + excel_data[selected_options['select_8_3']].astype(str) + '!' + excel_data[selected_options['select_8_4']].astype(str)

                            ssdv = pd.concat([excel_data[selected_options['select_7_1']], excel_data[selected_options['select_7_2']], 
                                excel_data[selected_options['select_8_3']],  excel_data[selected_options['select_8_4']], combined], axis=1, 
                                keys=[selected_options['select_8_1'], selected_options['select_8_2'], selected_options['select_8_3'], 
                                selected_options['select_8_4'], 'Combined'])

                            ssdv.to_excel(excel_writer, sheet_name='SSD-V', index=False)

                        # If SSR-R Checked
                        if item == 'checkbox_SSD-V':
                            combined = excel_data[selected_options['select_9_1']].astype(str) + '!' + excel_data[selected_options['select_9_2']].astype(str) + '!' + excel_data[selected_options['select_9_3']].astype(str) + '!' + excel_data[selected_options['select_9_4']].astype(str)

                            ssrr = pd.concat([excel_data[selected_options['select_9_1']], excel_data[selected_options['select_9_2']], 
                                excel_data[selected_options['select_9_3']],  excel_data[selected_options['select_9_4']], combined], axis=1, 
                                keys=[selected_options['select_9_1'], selected_options['select_9_2'], selected_options['select_9_3'], 
                                selected_options['select_9_4'], 'Combined'])

                            ssrr.to_excel(excel_writer, sheet_name='SSR-R', index=False)
                    
                    # Save the Excel file
                    excel_writer.close()
                    messages.success(request, f'Output has generated! Check D:/Output.xlsx')
                    error_occurred = True
                    key_to_remove = 'uploaded_file_name'

                    if key_to_remove in context:        
                        del context['uploaded_file_name']
                        del context['columns']
                        cache.delete('excel_data')
                else:
                    messages.warning(request, f'Please, Select the Checkname!')
                    error_occurred = True

        except KeyError as e:
            messages.error(request, f'Please, Select the Column!')
            error_occurred = True
        except PermissionError:
            messages.error(request, f'Permission denied: The file may currently be in use on your system!')
            error_occurred = True

    if error_occurred:
        return render(request, 'index.html', context)
    
    return HttpResponse(status=204)