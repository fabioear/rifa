import React, { useEffect, useState } from 'react';

interface PasswordStrengthProps {
    password: string;
    onValidationChange: (isValid: boolean) => void;
}

const PasswordStrength: React.FC<PasswordStrengthProps> = ({ password, onValidationChange }) => {
    const [requirements, setRequirements] = useState({
        length: false,
        uppercase: false,
        number: false,
        special: false,
    });

    useEffect(() => {
        const checks = {
            length: password.length >= 6,
            uppercase: /[A-Z]/.test(password),
            number: /[0-9]/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password),
        };
        setRequirements(checks);

        const allValid = Object.values(checks).every(Boolean);
        onValidationChange(allValid);
    }, [password, onValidationChange]);

    const strengthScore = Object.values(requirements).filter(Boolean).length;
    
    const getStrengthColor = () => {
        if (strengthScore <= 1) return 'bg-red-500';
        if (strengthScore <= 3) return 'bg-yellow-500';
        return 'bg-green-500';
    };

    const getStrengthLabel = () => {
        if (strengthScore <= 1) return 'Fraca';
        if (strengthScore <= 3) return 'Média';
        return 'Forte';
    };

    return (
        <div className="mt-2 space-y-2">
            {/* Strength Bar */}
            <div className="h-1.5 w-full bg-gray-200 rounded-full overflow-hidden dark:bg-gray-700">
                <div 
                    className={`h-full transition-all duration-300 ${getStrengthColor()}`} 
                    style={{ width: `${(strengthScore / 4) * 100}%` }}
                />
            </div>
            
            {password.length > 0 && (
                <p className={`text-xs text-right font-medium ${
                    strengthScore <= 1 ? 'text-red-500' : 
                    strengthScore <= 3 ? 'text-yellow-500' : 'text-green-500'
                }`}>
                    {getStrengthLabel()}
                </p>
            )}

            {/* Requirements List */}
            <ul className="text-xs space-y-1 mt-2">
                <RequirementItem met={requirements.length} label="Mínimo 6 caracteres" />
                <RequirementItem met={requirements.uppercase} label="Uma letra maiúscula" />
                <RequirementItem met={requirements.number} label="Um número" />
                <RequirementItem met={requirements.special} label="Um caractere especial" />
            </ul>
        </div>
    );
};

const RequirementItem: React.FC<{ met: boolean; label: string }> = ({ met, label }) => (
    <li className={`flex items-center space-x-2 ${met ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'}`}>
        <span>{met ? '✅' : '⚪'}</span>
        <span>{label}</span>
    </li>
);

export default PasswordStrength;
