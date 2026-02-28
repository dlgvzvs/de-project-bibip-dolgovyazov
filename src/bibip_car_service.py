from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale
from pydantic import BaseModel
import os
import datetime
import decimal

class CarService:
    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path
        self.model_index = [] # добавил пустой список индексов моделей

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model: 
        os.makedirs(self.root_directory_path, exist_ok=True)
        
        with open(f'{self.root_directory_path}/models.txt', 'a', encoding = 'utf-8') as file:
            file.write(f'{model.id};{model.name};{model.brand}\n')
        
        current_line_number = sum(1 for line in open(f'{self.root_directory_path}/models.txt')) # исправил путь к файлу
        with open(f'{self.root_directory_path}/models_index.txt', 'a', encoding = 'utf-8') as file:
            file.write(f'{model.id};{current_line_number}\n')

        self.model_index.append((model.id, current_line_number)) # заполнил список индексов моделей

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        
        with open(f'{self.root_directory_path}/cars.txt', 'a', encoding = 'utf-8') as file:
            file.write(f'{car.vin};{car.model};{car.price};{car.date_start};{car.status}\n') # добавил \n, чтобы не получать 45 элементов в одной строке
        
        current_line_number = sum(1 for line in open(f'{self.root_directory_path}/cars.txt'))
        with open(f'{self.root_directory_path}/cars_index.txt', 'a', encoding='utf-8') as file: # исправил путь к файлу
            file.write(f'{car.vin};{current_line_number}\n') # добавил \n

    # Задание 2. Сохранение продаж.
    # Была ошибка No value for argument 'sales_date' in method call
    # Убираю лишний параметр из sell_car()
    def sell_car(self, sale: Sale,) -> Car:
        with open(f'{self.root_directory_path}/sales.txt', 'a', encoding = 'utf-8') as file:
            file.write(f'{sale.sales_number};{sale.car_vin};{sale.cost};{sale.sales_date}\n')

        current_line_number = sum(1 for line in open(f'{self.root_directory_path}/sales.txt'))
        with open(f'{self.root_directory_path}/sales_index.txt', 'a', encoding = 'utf-8') as file:
            file.write(f'{sale.sales_number};{current_line_number}\n')

        updated_lines = []
        with open(f'{self.root_directory_path}/cars.txt', 'r', encoding='utf-8') as file: # исправил путь к файлу
            lines = file.readlines()
            for line in lines:
                vin, model, price, date_start, status = line.strip().split(';')
                if vin == sale.car_vin:
                    status = 'sold'
                updated_lines.append(f'{vin};{model};{price};{date_start};{status}\n')

        with open(f'{self.root_directory_path}/cars.txt', 'w', encoding='utf-8') as file:
            file.writelines(updated_lines)

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        available_cars = []
        with open(f'{self.root_directory_path}/cars.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                vin, model, price, date_start, car_status = line.strip().split(';')
                if status == 'available':
                    car = Car( # добавляю локальную переменную, чтобы собрать объект Car
                    vin=vin,
                    model=model,
                    price=decimal.Decimal(price),
                    date_start=datetime.datetime.fromisoformat(date_start),
                    car_status=status
            )
                    available_cars.append(car) # собираю список доступных машин из объектов Car, используя переменную car
        return available_cars

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        line_number = None 
        with open(f'{self.root_directory_path}/cars_index.txt', 'r', encoding='utf-8') as reading_indexes:
            for line in reading_indexes:
                current_vin, current_line_number = line.strip().split(';')
                if current_vin == vin:
                  line_number = int(current_line_number)
                break

        if line_number is None:
            return None

        with open(f'{self.root_directory_path}/cars.txt', 'r', encoding='utf-8') as reading_cars:
            lines = reading_cars.readlines()
            if 0 <= int(line_number) < len(lines):
                vin_car, model_id, price, date_start, status = lines[line_number].strip().split(';') # делаю парсинг данных по столбцам
            else:
                return None

        model_info = self.read_model_info(model_id) # обращаюсь к следующему методу, чтобы взять оттуда нужную информацию
        if model_info is None:
            return None

        model_id_from_file, model_name, model_brand = model_info.split(';') # беру отсюда id, имя модели и имя бренда

        return CarFullInfo( #так как класс определён ранее, то здесь я просто создаю объекты класса
        vin=vin_car,
        car_model_name=model_name,
        car_model_brand=model_brand,
        price=decimal.Decimal(price),
        date_start=datetime.datetime.fromisoformat(date_start),
        status=status,
        sales_date=None,
        sales_cost=None
    )

    def read_model_info(self, model_id: str) -> str | None:
        line_number = None
        with open(f'{self.root_directory_path}/models_index.txt', 'r', encoding='utf-8') as file:
            for line in file:
                id, current_line_number = line.strip().split(';')
                if id == model_id:
                    line_number = int(current_line_number)
                    break
        if line_number is None:
                    return None

        with open(f'{self.root_directory_path}/models.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            if 0 <= int(line_number) < len(lines):
                model_id_from_file, name, brand = lines[line_number].strip().split(';') # снова делаю парсинг
                return f'{model_id_from_file};{name};{brand}' # сохраняю успешно найденное значение
            else:
                return None

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        line_number = None
        with open(f'{self.root_directory_path}/cars_index.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                current_vin, current_line_number = line.strip().split(';')
                if current_vin == vin:
                    line_number = int(current_line_number)
                    break

        with open(f'{self.root_directory_path}/cars.txt', 'r', encoding='utf-8') as file: # сначала просто читаю файл
            all_lines = file.readlines()
            
        with open(f'{self.root_directory_path}/cars.txt', 'w', encoding='utf-8') as file: # открываю в режиме записи
            for i, line in enumerate(all_lines):
                if i == int(line_number):
                    vin, model, price, date_start, status = line.strip().split(';')
                    all_lines[i] = f'{new_vin};{model};{price};{date_start};{status}\n'
                    break
            file.writelines(all_lines)

        with open(f'{self.root_directory_path}/cars_index.txt', 'w', encoding='utf-8') as file:
            all_lines = file.readlines()
            for i, line in enumerate(all_lines):
                current_vin, line_number = line.strip().split(';')
                if current_vin == vin:
                    all_lines[i] = f'{new_vin};{line_number}\n'
                break
            file.writelines(all_lines)

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        with open(f'{self.root_directory_path}/sales.txt', 'r', encoding='utf-8') as file:
            sales_lines = file.readlines()
            is_deleted_header = 'is_deleted;' + sales_lines[0].strip() + '\n'
            sales_lines[0] = is_deleted_header
            
            for i in range (1,len(sales_lines)):
                line = sales_lines[i].strip()
                if sales_number in line:
                    sales_lines[i] = f'True;{line}\n'
                else:
                    sales_lines[i] = f'False;{line}\n'
                
        with open(f'{self.root_directory_path}/sales.txt', 'w', encoding='utf-8') as file:
            file.writelines(sales_lines)


    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        sales_by_model_id = {}
        with open(f'{self.root_directory_path}/sales.txt', 'r', encoding='utf-8') as file:
            sales_lines = file.readlines()
            for line in sales_lines:
                components = line.strip().split(';')
                model_id = components[1]
                if model_id in sales_by_model_id:
                    sales_by_model_id[model_id] += 1
                else:
                    sales_by_model_id[model_id] = 1
