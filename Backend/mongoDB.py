from pymongo import MongoClient
from datetime import datetime,timedelta
from collections import defaultdict 

def connection_data_base(id_bag,variety,cuttings,block,harvester,cuting_bag,base_sheet,long_stem,
                         short_stem,average_length,average_diameter,date):
    try:
        client =  MongoClient('localhost',27017)
        database = client['Cutting_vision']
        collection  = database['date_harvester']

        collection.insert_one({
        "id_bag": id_bag,
        "variety": variety,
        "cuttings": cuttings,
        "block": block,
        "harvester": harvester,
        "cutting_bag": cuting_bag,
        "base_sheet": base_sheet,
        "long_stem": long_stem,
        "short_stem": short_stem,
        "average_length": average_length,
        "average_diameter": average_diameter,
        "date": date
        })

    except Exception as ex:
        print('Error durantre la conexion')
    finally:
        print('Conexion finalizada...')

def count_harvester_records(harvester, date):
    print('Cosechado0000r = ', harvester)
    print('Cosechado0000r = ', harvester)
    print('Cosechado0000r = ', harvester)
    count_Cutting_bag = 0
    count_base_sheet  = 0
    count_long_stem =  0 
    count_short_stem =  0
    sum_average_length = 0
    sum_average_diameter  =  0
    try:
        # Conectar al servidor MongoDB
        client = MongoClient('localhost', 27017)
        database = client['Cutting_vision']
        collection = database['date_harvester']

        # Convertir la fecha en cadena si es necesario
        if isinstance(date, datetime):
            date = date.strftime('%d/%m/%Y')

        # Crear la consulta
        query = {
            "harvester": harvester,
            "date": date
        }
        # Contar el número de documentos que coinciden con la consulta
        count = collection.count_documents(query)
        print(f'Número de registros para el recolector {harvester} en la fecha {date}: {count}')
        
        if count == 0 :
            count_Cutting_bag = 0
            count_base_sheet = 0
            count_long_stem = 0
            count_short_stem = 0
            sum_average_length = 0
            sum_average_diameter = 0
            average_diameter_day = 0 
            average_length_day = 0

        elif count != 0:
            records = collection.find(query)
            # Iterar sobre los documentos y acceder a los campos específicos
            for record in records:
                count_Cutting_bag = count_Cutting_bag + record['cutting_bag']
                count_base_sheet = count_base_sheet + record.get("base_sheet")
                count_long_stem = count_long_stem + record.get("long_stem")
                count_short_stem = count_short_stem + record.get("short_stem")
                sum_average_length = sum_average_length + record.get("average_length")
                sum_average_diameter = sum_average_diameter + record.get("average_diameter")

            average_length_day = (sum_average_length/count)
            average_diameter_day = (sum_average_diameter/count)
        print('Conteo de esquejes en el dia: ', count_Cutting_bag)
        print('Conte haja en base en el dia:  ', count_base_sheet)
        print('Conteo de tallos largos en el dia: ', count_long_stem )
        print('Conteo de tallos cortos en el dia: ',count_short_stem)
        print('Promedio de la longitud de esqejes del dia: ', average_length_day)
        print('Promedio de los diametros de los esqejes del dia: ', average_diameter_day)

        return count,count_Cutting_bag,count_base_sheet,count_long_stem,count_short_stem,average_length_day,average_diameter_day

    except Exception as ex:
        print(f'Error durante la conexión o consulta: {ex}')
        return None
    
    finally:
        client.close()
        print('Conexión cerrada')

def get_start_of_week(date):
    # Obtener el lunes de la semana para la fecha dada
    start_of_week = date - timedelta(days=date.weekday())
    print('Start of week', start_of_week)
    return start_of_week

def count_harvester_records_week(harvester, date):
    count_Cutting_bag_w = 0
    count_base_sheet_w = 0
    count_long_stem_w = 0
    count_short_stem_w = 0
    sum_average_length = 0
    sum_average_diameter = 0
    try:
        # Conectar al servidor MongoDB
        client = MongoClient('localhost', 27017)
        database = client['Cutting_vision']
        collection = database['date_harvester']

        # Convertir la fecha en objeto datetime si es necesario
        if isinstance(date, str):
            date = datetime.strptime(date, '%d/%m/%Y')

        # Obtener el lunes de la semana actual
        start_of_week = get_start_of_week(date)
        end_of_week = date

        # Crear la consulta
        query = {
            "harvester": harvester,
            "date": {
                "$gte": start_of_week.strftime('%d/%m/%Y'),
                "$lte": end_of_week.strftime('%d/%m/%Y')
            }
        }

        # Contar el número de documentos que coinciden con la consulta
        countW = collection.count_documents(query)
        print(f'Número de registros para el recolector {harvester} desde {start_of_week.strftime("%d/%m/%Y")} hasta {end_of_week.strftime("%d/%m/%Y")}: {countW}')
        
        if countW == 0:
            print('No se encontraron registros para la consulta especificada.')
            return 0, 0, 0, 0, 0, 0, 0

        records = collection.find(query)
        # Iterar sobre los documentos y acceder a los campos específicos
        for record in records:
            count_Cutting_bag_w += record.get('cutting_bag', 0)
            count_base_sheet_w += record.get('base_sheet', 0)
            count_long_stem_w += record.get('long_stem', 0)
            count_short_stem_w += record.get('short_stem', 0)
            sum_average_length += record.get('average_length', 0)
            sum_average_diameter += record.get('average_diameter', 0)

        average_length_week = sum_average_length / countW
        average_diameter_week = sum_average_diameter / countW

        print('Conteo de esquejes en la semana: ', count_Cutting_bag_w)
        print('Conteo de hojas en base en la semana: ', count_base_sheet_w)
        print('Conteo de tallos largos en la semana: ', count_long_stem_w)
        print('Conteo de tallos cortos en la semana: ', count_short_stem_w)
        print('Promedio de la longitud de esquejes en la semana: ', average_length_week)
        print('Promedio de los diámetros de los esquejes en la semana: ', average_diameter_week)

        return countW, count_Cutting_bag_w,count_base_sheet_w, count_long_stem_w, count_short_stem_w, average_length_week, average_diameter_week

    except Exception as ex:
        print(f'Error durante la conexión o consulta: {ex}')
        return None
    
    finally:
        client.close()
        print('Conexión cerrada')

def query_data(harvester, date_str):
    # Diccionario para almacenar resultados agrupados por variedad
    variety_groups = defaultdict(lambda: {
        "records": [],
        "count_Cutting_bag": 0,
        "count_base_sheet": 0,
        "count_long_stem": 0,
        "count_short_stem": 0,
        "sum_average_length": 0.0,
        "sum_average_diameter": 0.0
    })
    
    try:
        # Conectar al servidor MongoDB
        client = MongoClient('localhost', 27017)
        database = client['Cutting_vision']
        collection = database['date_harvester']
        
        # Verificar y convertir la fecha de cadena a objeto datetime
        if isinstance(date_str, str):
            date = datetime.strptime(date_str, '%d/%m/%Y')
        
        # Definir la consulta
        query = {
            "harvester": harvester,
            "date": date_str  # Asumiendo que la fecha se almacena como cadena en este formato en la base de datos
        }
        
        # Realizar la consulta
        countW = collection.count_documents(query)
        
        # Imprimir el resultado del conteo
        print(f'Número de registros para el recolector {harvester} desde el día {date_str} son: {countW}')
        
        # Obtener y procesar los registros encontrados
        records = collection.find(query)
        
        for record in records:
            variety = record.get('variety', 'unknown')
            variety_groups[variety]["records"].append(record)
            
            # Actualizar las sumas y conteos para la variedad actual
            variety_groups[variety]["count_Cutting_bag"] += record.get("cutting_bag", 0)
            variety_groups[variety]["count_base_sheet"] += record.get("base_sheet", 0)
            variety_groups[variety]["count_long_stem"] += record.get("long_stem", 0)
            variety_groups[variety]["count_short_stem"] += record.get("short_stem", 0)
            variety_groups[variety]["sum_average_length"] += record.get("average_length", 0.0)
            variety_groups[variety]["sum_average_diameter"] += record.get("average_diameter", 0.0)
        
        num_groups = len(variety_groups)
        # Imprimir los grupos de variedades y sus estadísticas
        for variety, data in variety_groups.items():
            print(f"\nVariedad: {variety}")
            print(f"Total registros: {len(data['records'])}")
            print(f"Total Cutting Bag: {data['count_Cutting_bag']}")
            print(f"Total Base Sheet: {data['count_base_sheet']}")
            print(f"Total Long Stem: {data['count_long_stem']}")
            print(f"Total Short Stem: {data['count_short_stem']}")
            print(f"Sum Average Length: {data['sum_average_length']}")
            print(f"Sum Average Diameter: {data['sum_average_diameter']}")

        
        return num_groups,variety_groups
    
    except Exception as ex:
        print(f'Error durante la conexión o consulta: {ex}')
        return None
    
    finally:
        # Asegurar que la conexión se cierre
        client.close()
        print('Conexión cerrada')


            
        