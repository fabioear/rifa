import React, { ChangeEvent } from 'react';

interface CurrencyInputProps {
    value: string | number;
    onChange: (value: string) => void;
    placeholder?: string;
    className?: string;
    required?: boolean;
    disabled?: boolean;
    label?: string;
    id?: string;
}

export const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
    }).format(value);
};

const CurrencyInput: React.FC<CurrencyInputProps> = ({
    value,
    onChange,
    placeholder = 'R$ 0,00',
    className,
    required,
    disabled,
    id
}) => {
    // Converte o valor atual para exibir formatado
    const getDisplayValue = (val: string | number) => {
        if (!val) return '';
        const numberVal = typeof val === 'string' ? parseFloat(val) : val;
        if (isNaN(numberVal)) return '';
        return formatCurrency(numberVal);
    };

    const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
        // Remove tudo que não for dígito
        let rawValue = e.target.value.replace(/\D/g, '');
        
        // Se estiver vazio, retorna vazio ou zero
        if (!rawValue) {
            onChange('');
            return;
        }

        // Converte para float (ex: 123 -> 1.23)
        const floatValue = parseFloat(rawValue) / 100;
        
        // Retorna o valor numérico como string para o pai (ex: "1.23")
        // O pai deve guardar o valor "raw" (float ou string de float)
        onChange(floatValue.toFixed(2));
    };

    return (
        <input
            id={id}
            type="text"
            inputMode="numeric"
            value={getDisplayValue(value)}
            onChange={handleChange}
            placeholder={placeholder}
            className={className}
            required={required}
            disabled={disabled}
        />
    );
};

export default CurrencyInput;
