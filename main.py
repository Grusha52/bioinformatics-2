import pandas as pd
import numpy as np

# 1. Загрузка данных
file_path = 'student_33_2026-11-01-09-54_VEP.tsv'
df = pd.read_csv(file_path, sep='\t')

# Если VEP всё же выдал несколько строк на один вариант (несмотря на фильтры),
# оставляем только первую запись для каждого 'Uploaded_variation'
df_unique = df.drop_duplicates(subset=['Uploaded_variation']).copy()

# 2. Функции для обработки специфичных колонок
def get_transcript_rule(row):
    """Определяет правило выбора транскрипта по приоритету: MANE Select -> Canonical -> Other"""
    if pd.notnull(row.get('MANE_SELECT')) and 'MANE' in str(row.get('MANE_SELECT')):
        return 'MANE Select'
    elif pd.notnull(row.get('CANONICAL')) and str(row.get('CANONICAL')) == 'YES':
        return 'Canonical'
    return 'Other'

def get_clinvar_status(sig_val):
    """Определяет наличие записи в ClinVar (если есть интерпретация — значит запись есть)"""
    if pd.notnull(sig_val) and str(sig_val).strip() != '-':
        return 'Yes'
    return 'No'

# 3. Сборка итоговой таблицы
final_table = pd.DataFrame({
    'Исходный ID (Uploaded)': df_unique['Uploaded_variation'],
    'Ген': df_unique['SYMBOL'].fillna('-'),
    'Наиболее значимое последствие': df_unique['Consequence'],
    'Правило выбора транскрипта': df_unique.apply(get_transcript_rule, axis=1),
    'rsID': df_unique['Existing_variation'].fillna('-'),
    'gnomAD AF': df_unique['gnomAD_genomes_AF'].fillna('-'),
    'Наличие ClinVar': df_unique['ClinVar_CLNSIG'].apply(get_clinvar_status),
    # Убираем нижние подчеркивания из интерпретации для красивого вида
    'Интерпретация ClinVar': df_unique['ClinVar_CLNSIG'].fillna('-').astype(str).str.replace('_', ' ')
})

# 4. Сохранение результата
output_filename = 'final_variants_report.csv'
final_table.to_csv(output_filename, index=False, encoding='utf-8-sig')

print(f"Обработка завершена. Найдено уникальных вариантов: {len(final_table)}")
print(f"Результат сохранен в {output_filename}")

# Вывод первых 5 строк для проверки в консоли
print("\nПревью таблицы:")
print(final_table.head().to_markdown(index=False))