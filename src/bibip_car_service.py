# Внёс корректировки в индексацию строк, в принципе +- понял, что было не так.
# Пока процесс сохранения изменений и загрузки новой версии проекта отнимает куда больше времени и сил, чем сам проект,
# то кэша много, то терминал выдаёт ошибку, то на платформе пусто, то какое-то слияние локальной и удалённой ветки.
# Хотел бы попросить Вас оставить комментарии в целом по проекту, где у меня слабые места в знании Python,
# над чем мне нужно будет поработать, пока перехожу в другую когорту. Решил взять время на ликвидацию пробелов.

from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale
from pydantic import BaseModel
import os
import datetime
import decimal

class CarService:
    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path
        self.model_index = []

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model: 
        os.makedirs(self.root_directory_path, exist_ok=True)
        
        with open(f'{self.root_directory_path}/models.txt', 'a', encoding = 'utf-8') as file:
            file.write(f'{model.id};{model.name};{model.brand}\n')
        
        current_line_number = sum(1 for line in open(f'{self.root_directory_path}/models.txt'))
        with open(f'{self.root_directory_path}/models_index.txt', 'a', encoding = 'utf-8') as file:
            file.write(f'{model.id};{current_line_number}\n')

        self.model_index.append((model.id, current_line_number))

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        
        with open(f'{self.root_directory_path}/cars.txt', 'a', encoding = 'utf-8') as file:
            file.write(f'{car.vin};{car.model};{car.price};{car.date_start};{car.status}\n')
        
        current_line_number = sum(1 for line in open(f'{self.root_directory_path}/cars.txt'))
        with open(f'{self.root_directory_path}/cars_index.txt', 'a', encoding='utf-8') as file:
            file.write(f'{car.vin};{current_line_number}\n')

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale,) -> Car:
        with open(f'{self.root_directory_path}/sales.txt', 'a', encoding = 'utf-8') as file:
            file.write(f'{sale.sales_number};{sale.car_vin};{sale.cost};{sale.sales_date}\n')

        current_line_number = sum(1 for line in open(f'{self.root_directory_path}/sales.txt'))
        with open(f'{self.root_directory_path}/sales_index.txt', 'a', encoding = 'utf-8') as file:
            file.write(f'{sale.sales_number};{current_line_number}\n')

        updated_lines = []
        with open(f'{self.root_directory_path}/cars.txt', 'r', encoding='utf-8') as file:
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
                if car_status == status:
                    car = Car( 
                    vin=vin,
                    model=model,
                    price=decimal.Decimal(price),
                    date_start=datetime.datetime.fromisoformat(date_start),
                    status=car_status
            )
                    available_cars.append(car)
        return available_cars

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        line_number = None 
        with open(f'{self.root_directory_path}/cars_index.txt', 'r', encoding='utf-8') as reading_indexes:
            for line in reading_indexes:
                current_vin, current_line_number = line.strip().split(';')
                if current_vin == vin:
                    line_number = int(current_line_number)
                    break # подвинул отступ вправо

        if line_number is None:
            return None

        with open(f'{self.root_directory_path}/cars.txt', 'r', encoding='utf-8') as reading_cars:
            lines = reading_cars.readlines()
            if 0 <= int(line_number) < len(lines):
                vin_car, model_id, price, date_start, status = lines[line_number - 1].strip().split(';') # исправил индесацию строк
            else:
                return None

        model_info = self.read_model_info(model_id)
        if model_info is None:
            return None

        model_id_from_file, model_name, model_brand = model_info.split(';')

        sales_date = None
        sales_cost = None

        if status == 'sold':
            with open(f'{self.root_directory_path}/sales.txt', 'r', encoding='utf-8') as sales_file:
                sales_lines = sales_file.readlines()
                for sale_line in sales_lines:
                    sales_number, car_vin, cost, date = sale_line.strip().split(';')
                    if car_vin == vin_car:
                        sales_cost = decimal.Decimal(cost)
                        sales_date = datetime.datetime.fromisoformat(date)
                        break

        return CarFullInfo(
        vin=vin_car,
        car_model_name=model_name,
        car_model_brand=model_brand,
        price=decimal.Decimal(price),
        date_start=datetime.datetime.fromisoformat(date_start),
        status=status,
        sales_date=sales_date,
        sales_cost=sales_cost
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
                model_id_from_file, name, brand = lines[line_number-1].strip().split(';') # исправил индексацию строк
                return f'{model_id_from_file};{name};{brand}'
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

        with open(f'{self.root_directory_path}/cars.txt', 'r', encoding='utf-8') as file:
            all_lines = file.readlines()
            
        with open(f'{self.root_directory_path}/cars.txt', 'w', encoding='utf-8') as file:
            for i, line in enumerate(all_lines):
                if i == int(line_number):
                    vin, model, price, date_start, status = line.strip().split(';')
                    all_lines[i] = f'{new_vin};{model};{price};{date_start};{status}\n'
                    break
            file.writelines(all_lines)

        with open(f'{self.root_directory_path}/cars_index.txt', 'w', encoding='utf-8') as file:
            all_lines = file.readlines()
            for i, line in enumerate(all_lines, start=1): # добавил условие, что стартуем с единицы, а не нуля
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
