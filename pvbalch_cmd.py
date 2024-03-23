from pvbalch_computing_module import *
import json

#Создание объекта компонента для каждого из набора данных(хим.элементов)
#Входные данные включают вес компонента и процентное содержание элементов, 
#на основании которых при инициализации объекта автоматически рассчитывается вес каждого элемента
with open('data.json', 'r') as file:
    data = json.load(file)

compounds = [Compound(**comp_data) for comp_data in data]

#Суммарный полный вес всех компонентовы
total_weight = sum(compound.Weight for compound in compounds)

#Словарь, содержащий общий вес каждого элемента, собранный из всех компонентов
#В формате элемент:вес, типа {'Au':40.22, 'Cu':288.11}
total_elements = calculate_total_elements(compounds)

#Процентное соотношение каждого элемента в отношении к total_weight
element_percentages = calculate_element_percentages(total_elements, total_weight)

#Вычисления параметров штейна и шлака
stein_results = calculate_materials_in_stein(total_elements, total_weight, element_percentages)
slug_results = calculate_materials_in_slug(total_elements, stein_results)

print(f"Copper in Stein: {stein_results['Cu_in_stein_percentage']:.2f}%")
print(f"Iron in Stein: {stein_results['Fe_in_stein_percentage']:.2f}%")
print(f"Sulfur in Stein: {stein_results['S_in_stein_percentage']:.2f}%")
print(f"Gold Concentration in Stein: {slug_results['gold_concentration_stein']} ppm")
print(f"Silver Concentration in Stein: {slug_results['silver_concentration_stein']} ppm")
print('_____________________________________________')
stein_weight_percentage = stein_results['stein_weight']/total_weight*100
print(f"Stein weight: {stein_results['stein_weight']} ({stein_weight_percentage:.2f}%)\n")

print(f"SiO2 in Slag: {slug_results['SiO2_in_slag_percentage']:.2f}%")
print(f"CaO in Slag: {slug_results['CaO_in_slag_percentage']:.2f}%")
print(f"Al2O3 in Slag: {slug_results['Al2O3_in_slag_percentage']:.2f}%")
print(f"FeO in Slag: {slug_results['FeO_in_slag_percentage']:.2f}%")
print('_____________________________________________')
slag_weight_percentage = slug_results['slag_weight']/total_weight*100
print(f"Total Slag Weight: {slug_results['slag_weight']} ({slag_weight_percentage:.2f}%)\n")

#Вычисление весов и процентного соотношения общего сплава и остатка(возгон) 
melt_weight = stein_results['stein_weight'] + slug_results['slag_weight']
sublimates_weight = total_weight - stein_results['stein_weight'] - slug_results['slag_weight']

print(f"Melt weight: {melt_weight} ({melt_weight/total_weight*100:.2f}%)")
sublimates_weight_percentage=sublimates_weight/total_weight*100
print(f"Sublimates weight: {sublimates_weight}({sublimates_weight_percentage:.2f}%)")

#Проверяем общий вес и процентное соотшношение суммируя все результаты, для проверки вычислений
print(f"Total weight: {stein_results['stein_weight']+slug_results['slag_weight']+sublimates_weight} ({stein_weight_percentage+slag_weight_percentage+sublimates_weight_percentage:.2f}%)")

