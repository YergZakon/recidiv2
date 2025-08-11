import React, { useState } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import Button from '../common/Button';
import Input from '../common/Input';
import Card from '../common/Card';
import { UserIcon, CalendarIcon, UserGroupIcon } from '@heroicons/react/24/outline';

interface PersonFormData {
  full_name: string;
  birth_date: string;
  gender: 'M' | 'F';
  violations_count: number;
  last_violation_date: string;
  pattern: 'mixed_unstable' | 'chronic_criminal' | 'escalating' | 'deescalating' | 'single';
  criminal_count: number;
  admin_count: number;
}

interface PersonFormProps {
  onSubmit: (data: PersonFormData) => void;
  loading?: boolean;
}

const PersonForm: React.FC<PersonFormProps> = ({ onSubmit, loading = false }) => {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors }
  } = useForm<PersonFormData>({
    defaultValues: {
      gender: 'M',
      pattern: 'mixed_unstable',
      violations_count: 1,
      criminal_count: 0,
      admin_count: 1
    }
  });

  const watchViolationsCount = watch('violations_count', 1);

  const onSubmitForm: SubmitHandler<PersonFormData> = (data) => {
    onSubmit(data);
  };

  const patternOptions = [
    { value: 'mixed_unstable', label: 'Смешанный нестабильный (72.7%)' },
    { value: 'chronic_criminal', label: 'Хронический преступный (13.6%)' },
    { value: 'escalating', label: 'Эскалирующий (7.0%)' },
    { value: 'deescalating', label: 'Деэскалирующий (5.7%)' },
    { value: 'single', label: 'Единичные случаи (1.0%)' }
  ];

  return (
    <Card title="Ручной ввод данных лица" subtitle="Заполните форму для расчета риск-балла">
      <form onSubmit={handleSubmit(onSubmitForm)} className="space-y-6">
        {/* Основные данные */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="ФИО"
            placeholder="Иванов Иван Иванович"
            {...register('full_name', { 
              required: 'ФИО обязательно для заполнения',
              minLength: { value: 5, message: 'Минимум 5 символов' }
            })}
            error={errors.full_name?.message}
            leftIcon={<UserIcon className="h-5 w-5 text-gray-400" />}
          />

          <Input
            label="Дата рождения"
            type="date"
            {...register('birth_date', { 
              required: 'Дата рождения обязательна',
              validate: (value) => {
                const birthYear = new Date(value).getFullYear();
                const currentYear = new Date().getFullYear();
                const age = currentYear - birthYear;
                if (age < 18 || age > 80) {
                  return 'Возраст должен быть от 18 до 80 лет';
                }
                return true;
              }
            })}
            error={errors.birth_date?.message}
            leftIcon={<CalendarIcon className="h-5 w-5 text-gray-400" />}
          />
        </div>

        {/* Пол */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Пол
          </label>
          <div className="flex space-x-4">
            <label className="flex items-center">
              <input
                type="radio"
                value="M"
                {...register('gender', { required: 'Выберите пол' })}
                className="mr-2 text-crime-red focus:ring-crime-red"
              />
              Мужской
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="F"
                {...register('gender', { required: 'Выберите пол' })}
                className="mr-2 text-crime-red focus:ring-crime-red"
              />
              Женский
            </label>
          </div>
          {errors.gender && (
            <p className="mt-1 text-sm text-red-600">
              {typeof errors.gender.message === 'string' ? errors.gender.message : 'Неверное значение пола'}
            </p>
          )}
        </div>

        {/* Паттерн поведения */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Паттерн поведения
          </label>
          <select
            {...register('pattern', { required: 'Выберите паттерн поведения' })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-crime-blue focus:border-transparent"
          >
            {patternOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          {errors.pattern && (
            <p className="mt-1 text-sm text-red-600">
              {typeof errors.pattern.message === 'string' ? errors.pattern.message : 'Неверное значение паттерна'}
            </p>
          )}
        </div>

        {/* Данные о нарушениях */}
        <div className="bg-gray-50 p-4 rounded-lg space-y-4">
          <h4 className="font-medium text-gray-900 flex items-center">
            <UserGroupIcon className="h-5 w-5 mr-2 text-gray-500" />
            История нарушений
          </h4>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              label="Всего нарушений"
              type="number"
              min={0}
              max={20}
              {...register('violations_count', { 
                required: 'Укажите количество нарушений',
                min: { value: 0, message: 'Минимум 0 нарушений' },
                max: { value: 20, message: 'Максимум 20 нарушений' }
              })}
              error={errors.violations_count?.message}
            />

            <Input
              label="Уголовные дела"
              type="number"
              min={0}
              max={watchViolationsCount}
              {...register('criminal_count', { 
                required: 'Укажите количество уголовных дел',
                min: { value: 0, message: 'Минимум 0' },
                max: { 
                  value: watchViolationsCount, 
                  message: `Не более ${watchViolationsCount}` 
                }
              })}
              error={errors.criminal_count?.message}
            />

            <Input
              label="Административные"
              type="number"
              min={0}
              max={watchViolationsCount}
              {...register('admin_count', { 
                required: 'Укажите количество административных дел',
                min: { value: 0, message: 'Минимум 0' },
                max: { 
                  value: watchViolationsCount, 
                  message: `Не более ${watchViolationsCount}` 
                }
              })}
              error={errors.admin_count?.message}
            />
          </div>

          <Input
            label="Дата последнего нарушения"
            type="date"
            {...register('last_violation_date', { 
              required: 'Укажите дату последнего нарушения',
              validate: (value) => {
                const violationDate = new Date(value);
                const today = new Date();
                if (violationDate > today) {
                  return 'Дата не может быть в будущем';
                }
                const fiveYearsAgo = new Date();
                fiveYearsAgo.setFullYear(today.getFullYear() - 5);
                if (violationDate < fiveYearsAgo) {
                  return 'Нарушение не может быть старше 5 лет';
                }
                return true;
              }
            })}
            error={errors.last_violation_date?.message}
            leftIcon={<CalendarIcon className="h-5 w-5 text-gray-400" />}
          />
        </div>

        {/* Кнопка отправки */}
        <div className="flex justify-end space-x-4">
          <Button
            type="submit"
            loading={loading}
            disabled={loading}
          >
            Рассчитать риск
          </Button>
        </div>
      </form>
    </Card>
  );
};

export default PersonForm;