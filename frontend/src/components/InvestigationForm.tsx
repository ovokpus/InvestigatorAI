'use client';

import { useState } from 'react';

interface FormData {
  amount: number;
  currency: string;
  description: string;
  customer_name: string;
  account_type: string;
  risk_rating: string;
  country_to: string;
}

interface InvestigationFormProps {
  onSubmit: (formData: FormData) => void;
  isLoading: boolean;
}

export default function InvestigationForm({ onSubmit, isLoading }: InvestigationFormProps) {
  const [formData, setFormData] = useState({
    amount: '',
    currency: 'USD',
    description: '',
    customer_name: '',
    account_type: 'Business',
    risk_rating: 'Medium',
    country_to: ''
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Convert amount to number
    const submitData = {
      ...formData,
      amount: parseFloat(formData.amount) || 0
    };
    
    onSubmit(submitData);
  };

  const isFormValid = formData.amount && formData.customer_name && formData.country_to && formData.description;

  return (
    <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
        <div>
          <label htmlFor="amount" className="block text-xs sm:text-sm font-medium text-contrast mb-1 sm:mb-2">
            Transaction Amount *
          </label>
          <input
            type="number"
            id="amount"
            name="amount"
            value={formData.amount}
            onChange={handleChange}
            placeholder="e.g., 75000"
            min="0"
            step="0.01"
            required
            className="w-full h-10 sm:h-auto text-sm sm:text-base"
          />
        </div>
        
        <div>
          <label htmlFor="currency" className="block text-xs sm:text-sm font-medium text-contrast mb-1 sm:mb-2">
            Currency
          </label>
          <select
            id="currency"
            name="currency"
            value={formData.currency}
            onChange={handleChange}
            className="w-full h-10 sm:h-auto text-sm sm:text-base"
          >
            <option value="USD">USD - US Dollar</option>
            <option value="EUR">EUR - Euro</option>
            <option value="GBP">GBP - British Pound</option>
            <option value="JPY">JPY - Japanese Yen</option>
            <option value="CAD">CAD - Canadian Dollar</option>
            <option value="AUD">AUD - Australian Dollar</option>
            <option value="CHF">CHF - Swiss Franc</option>
            <option value="CNY">CNY - Chinese Yuan</option>
          </select>
        </div>
      </div>

      <div>
        <label htmlFor="customer_name" className="block text-xs sm:text-sm font-medium text-contrast mb-1 sm:mb-2">
          Customer/Company Name *
        </label>
        <input
          type="text"
          id="customer_name"
          name="customer_name"
          value={formData.customer_name}
          onChange={handleChange}
          placeholder="e.g., Global Trading LLC"
          required
          className="w-full h-10 sm:h-auto text-sm sm:text-base"
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-xs sm:text-sm font-medium text-contrast mb-1 sm:mb-2">
          Transaction Description *
        </label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="e.g., Business payment to overseas supplier for industrial equipment"
          required
          rows={3}
          className="w-full resize-none text-sm sm:text-base min-h-[80px] sm:min-h-[90px]"
        />
      </div>

      <div>
        <label htmlFor="country_to" className="block text-xs sm:text-sm font-medium text-contrast mb-1 sm:mb-2">
          Destination Country *
        </label>
        <input
          type="text"
          id="country_to"
          name="country_to"
          value={formData.country_to}
          onChange={handleChange}
          placeholder="e.g., UAE, China, Russia"
          required
          className="w-full h-10 sm:h-auto text-sm sm:text-base"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
        <div>
          <label htmlFor="account_type" className="block text-xs sm:text-sm font-medium text-contrast mb-1 sm:mb-2">
            Account Type
          </label>
          <select
            id="account_type"
            name="account_type"
            value={formData.account_type}
            onChange={handleChange}
            className="w-full h-10 sm:h-auto text-sm sm:text-base"
          >
            <option value="Business">Business</option>
            <option value="Personal">Personal</option>
            <option value="Corporate">Corporate</option>
            <option value="Government">Government</option>
            <option value="Non-Profit">Non-Profit</option>
          </select>
        </div>
        
        <div>
          <label htmlFor="risk_rating" className="block text-xs sm:text-sm font-medium text-contrast mb-1 sm:mb-2">
            Initial Risk Rating
          </label>
          <select
            id="risk_rating"
            name="risk_rating"
            value={formData.risk_rating}
            onChange={handleChange}
            className="w-full h-10 sm:h-auto text-sm sm:text-base"
          >
            <option value="Low">Low Risk</option>
            <option value="Medium">Medium Risk</option>
            <option value="High">High Risk</option>
            <option value="Critical">Critical Risk</option>
          </select>
        </div>
      </div>

      <div className="pt-3 sm:pt-4">
        <button
          type="submit"
          disabled={!isFormValid || isLoading}
          className={`w-full btn-primary py-3 sm:py-4 px-4 sm:px-6 rounded-lg font-medium transition-all duration-200 text-sm sm:text-base min-h-[48px] sm:min-h-[52px] ${
            !isFormValid || isLoading
              ? 'opacity-50 cursor-not-allowed'
              : 'hover:shadow-lg active:scale-[0.98]'
          }`}
        >
          {isLoading ? (
            <div className="flex items-center justify-center space-x-2">
              <div className="animate-spin w-4 h-4 sm:w-5 sm:h-5 border-2 border-primary-foreground border-t-transparent rounded-full"></div>
              <span>Investigating...</span>
            </div>
          ) : (
            'Start Investigation'
          )}
        </button>
      </div>

      {!isFormValid && (
        <p className="text-xs sm:text-sm text-muted-foreground text-center px-2">
          Please fill in all required fields (marked with *) to start the investigation.
        </p>
      )}
    </form>
  );
}