'use client';

import { useState } from 'react';

// Unified form data interface supporting all investigation types
interface UnifiedFormData {
  // Investigation type routing
  investigation_type: 'fraud_transaction' | 'entity_research' | 'academic_research' | 'general_research';
  
  // Fraud investigation fields
  amount?: number;
  currency?: string;
  description?: string;
  customer_name?: string;
  account_type?: string;
  risk_rating?: string;
  country_to?: string;
  
  // Research investigation fields
  topic?: string;
  entity_name?: string;
  entity_type?: string;
  field?: string;
  context?: string;
  include_market_analysis?: boolean;
  
  // Common fields
  priority?: string;
}

interface UnifiedInvestigationFormProps {
  onSubmit: (formData: UnifiedFormData) => void;
  isLoading: boolean;
}

export default function UnifiedInvestigationForm({ onSubmit, isLoading }: UnifiedInvestigationFormProps) {
  const [investigationType, setInvestigationType] = useState<UnifiedFormData['investigation_type']>('fraud_transaction');
  const [formData, setFormData] = useState<Record<string, string | number | boolean>>({
    // Fraud defaults
    amount: '',
    currency: 'USD',
    description: '',
    customer_name: '',
    account_type: 'Business',
    risk_rating: 'Medium',
    country_to: '',
    // Research defaults
    topic: '',
    entity_name: '',
    entity_type: 'company',
    field: 'general',
    context: '',
    include_market_analysis: false,
    priority: 'normal'
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));
  };

  const handleInvestigationTypeChange = (type: UnifiedFormData['investigation_type']) => {
    setInvestigationType(type);
    // Reset form when changing investigation type
    setFormData({
      amount: '',
      currency: 'USD',
      description: '',
      customer_name: '',
      account_type: 'Business',
      risk_rating: 'Medium',
      country_to: '',
      topic: '',
      entity_name: '',
      entity_type: 'company',
      field: 'general',
      context: '',
      include_market_analysis: false,
      priority: 'normal'
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Create unified submission data based on investigation type
    const submitData: UnifiedFormData = {
      investigation_type: investigationType,
      priority: typeof formData.priority === 'string' ? formData.priority : 'normal'
    };

    // Add type-specific fields with type safety
    if (investigationType === 'fraud_transaction') {
      submitData.amount = parseFloat(String(formData.amount)) || 0;
      submitData.currency = String(formData.currency || 'USD');
      submitData.description = String(formData.description || '');
      submitData.customer_name = String(formData.customer_name || '');
      submitData.account_type = String(formData.account_type || 'Business');
      submitData.risk_rating = String(formData.risk_rating || 'Medium');
      submitData.country_to = String(formData.country_to || '');
    } else if (investigationType === 'entity_research') {
      submitData.entity_name = String(formData.entity_name || '');
      submitData.entity_type = String(formData.entity_type || 'company');
      submitData.context = String(formData.context || '');
      submitData.include_market_analysis = Boolean(formData.include_market_analysis);
    } else if (investigationType === 'academic_research') {
      submitData.topic = String(formData.topic || '');
      submitData.field = String(formData.field || 'general');
      submitData.context = String(formData.context || '');
    } else if (investigationType === 'general_research') {
      submitData.topic = String(formData.topic || '');
      submitData.context = String(formData.context || '');
    }
    
    onSubmit(submitData);
  };

  // Form validation based on investigation type
  const isFormValid = () => {
    switch (investigationType) {
      case 'fraud_transaction':
        return formData.amount && formData.customer_name && formData.country_to && formData.description;
      case 'entity_research':
        return formData.entity_name;
      case 'academic_research':
        return formData.topic && formData.field;
      case 'general_research':
        return formData.topic;
      default:
        return false;
    }
  };

  const investigationTypes = [
    {
      value: 'fraud_transaction',
      label: '🚨 Fraud Transaction',
      description: 'Comprehensive fraud analysis using multi-agent system'
    },
    {
      value: 'entity_research',
      label: '🏢 Entity Research',
      description: 'Financial entity investigation with AML/compliance focus'
    },
    {
      value: 'academic_research',
      label: '🎓 Academic Research',
      description: 'Scientific literature analysis and methodology extraction'
    },
    {
      value: 'general_research',
      label: '🔍 General Research',
      description: 'Iterative quality-driven research with multiple sources'
    }
  ];

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Investigation Type Selector */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
        <label className="block text-sm font-medium text-blue-800 dark:text-blue-200 mb-3">
          Investigation Type *
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {investigationTypes.map((type) => (
            <button
              key={type.value}
              type="button"
              onClick={() => handleInvestigationTypeChange(type.value as UnifiedFormData['investigation_type'])}
              className={`p-3 rounded-lg border text-left transition-all duration-200 ${
                investigationType === type.value
                  ? 'bg-primary text-primary-foreground border-primary shadow-md'
                  : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:border-primary hover:shadow-sm'
              }`}
            >
              <div className="font-medium text-sm">{type.label}</div>
              <div className="text-xs opacity-75 mt-1">{type.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Fraud Transaction Fields */}
      {investigationType === 'fraud_transaction' && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="amount" className="block text-sm font-medium text-contrast mb-2">
                Transaction Amount *
              </label>
                          <input
              type="number"
              id="amount"
              name="amount"
              value={String(formData.amount)}
              onChange={handleChange}
              placeholder="e.g., 75000"
              min="0"
              step="0.01"
              required
              className="w-full"
            />
            </div>
            
            <div>
              <label htmlFor="currency" className="block text-sm font-medium text-contrast mb-2">
                Currency
              </label>
              <select
                id="currency"
                name="currency"
                value={String(formData.currency)}
                onChange={handleChange}
                className="w-full"
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
            <label htmlFor="customer_name" className="block text-sm font-medium text-contrast mb-2">
              Customer/Company Name *
            </label>
                      <input
            type="text"
            id="customer_name"
            name="customer_name"
            value={String(formData.customer_name)}
            onChange={handleChange}
            placeholder="e.g., Global Trading LLC"
            required
            className="w-full"
          />
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium text-contrast mb-2">
              Transaction Description *
            </label>
            <textarea
              id="description"
              name="description"
              value={String(formData.description)}
              onChange={handleChange}
              placeholder="e.g., Business payment to overseas supplier for industrial equipment"
              required
              rows={3}
              className="w-full resize-none"
            />
          </div>

          <div>
            <label htmlFor="country_to" className="block text-sm font-medium text-contrast mb-2">
              Destination Country *
            </label>
            <input
              type="text"
              id="country_to"
              name="country_to"
              value={String(formData.country_to)}
              onChange={handleChange}
              placeholder="e.g., UAE, China, Russia"
              required
              className="w-full"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="account_type" className="block text-sm font-medium text-contrast mb-2">
                Account Type
              </label>
              <select
                id="account_type"
                name="account_type"
                value={String(formData.account_type)}
                onChange={handleChange}
                className="w-full"
              >
                <option value="Business">Business</option>
                <option value="Personal">Personal</option>
                <option value="Corporate">Corporate</option>
                <option value="Government">Government</option>
                <option value="Non-Profit">Non-Profit</option>
              </select>
            </div>
            
            <div>
              <label htmlFor="risk_rating" className="block text-sm font-medium text-contrast mb-2">
                Initial Risk Rating
              </label>
              <select
                id="risk_rating"
                name="risk_rating"
                value={String(formData.risk_rating)}
                onChange={handleChange}
                className="w-full"
              >
                <option value="Low">Low Risk</option>
                <option value="Medium">Medium Risk</option>
                <option value="High">High Risk</option>
                <option value="Critical">Critical Risk</option>
              </select>
            </div>
          </div>
        </>
      )}

      {/* Entity Research Fields */}
      {investigationType === 'entity_research' && (
        <>
          <div>
            <label htmlFor="entity_name" className="block text-sm font-medium text-contrast mb-2">
              Entity/Company Name *
            </label>
            <input
              type="text"
              id="entity_name"
              name="entity_name"
              value={String(formData.entity_name)}
              onChange={handleChange}
              placeholder="e.g., Suspicious Corp, John Doe"
              required
              className="w-full"
            />
          </div>

          <div>
            <label htmlFor="entity_type" className="block text-sm font-medium text-contrast mb-2">
              Entity Type
            </label>
            <select
              id="entity_type"
              name="entity_type"
              value={String(formData.entity_type)}
              onChange={handleChange}
              className="w-full"
            >
              <option value="company">Company/Corporation</option>
              <option value="individual">Individual Person</option>
              <option value="partnership">Partnership</option>
              <option value="trust">Trust/Foundation</option>
              <option value="government">Government Entity</option>
            </select>
          </div>

          <div>
            <label htmlFor="context" className="block text-sm font-medium text-contrast mb-2">
              Investigation Context
            </label>
            <textarea
              id="context"
              name="context"
              value={String(formData.context)}
              onChange={handleChange}
              placeholder="e.g., Money laundering investigation, sanctions screening, compliance check"
              rows={3}
              className="w-full resize-none"
            />
          </div>

          <div className="flex items-center space-x-3">
            <input
              type="checkbox"
              id="include_market_analysis"
              name="include_market_analysis"
              checked={Boolean(formData.include_market_analysis)}
              onChange={handleChange}
              className="w-4 h-4"
            />
            <label htmlFor="include_market_analysis" className="text-sm font-medium text-contrast">
              Include market analysis and competitive intelligence
            </label>
          </div>
        </>
      )}

      {/* Academic Research Fields */}
      {investigationType === 'academic_research' && (
        <>
          <div>
            <label htmlFor="topic" className="block text-sm font-medium text-contrast mb-2">
              Research Topic *
            </label>
            <input
              type="text"
              id="topic"
              name="topic"
              value={String(formData.topic)}
              onChange={handleChange}
              placeholder="e.g., Machine Learning in Fraud Detection, AML Regulatory Compliance"
              required
              className="w-full"
            />
          </div>

          <div>
            <label htmlFor="field" className="block text-sm font-medium text-contrast mb-2">
              Academic Field *
            </label>
            <select
              id="field"
              name="field"
              value={String(formData.field)}
              onChange={handleChange}
              className="w-full"
            >
              <option value="computer_science">Computer Science</option>
              <option value="finance">Finance</option>
              <option value="economics">Economics</option>
              <option value="law">Law</option>
              <option value="criminology">Criminology</option>
              <option value="statistics">Statistics</option>
              <option value="business">Business</option>
              <option value="general">General/Interdisciplinary</option>
            </select>
          </div>

          <div>
            <label htmlFor="context" className="block text-sm font-medium text-contrast mb-2">
              Research Context
            </label>
            <textarea
              id="context"
              name="context"
              value={String(formData.context)}
              onChange={handleChange}
              placeholder="e.g., Literature review for compliance project, methodology research, recent developments"
              rows={3}
              className="w-full resize-none"
            />
          </div>
        </>
      )}

      {/* General Research Fields */}
      {investigationType === 'general_research' && (
        <>
          <div>
            <label htmlFor="topic" className="block text-sm font-medium text-contrast mb-2">
              Research Topic *
            </label>
            <input
              type="text"
              id="topic"
              name="topic"
              value={String(formData.topic)}
              onChange={handleChange}
              placeholder="e.g., Cryptocurrency regulations, Trade sanctions impact, Financial crime trends"
              required
              className="w-full"
            />
          </div>

          <div>
            <label htmlFor="context" className="block text-sm font-medium text-contrast mb-2">
              Research Context
            </label>
            <textarea
              id="context"
              name="context"
              value={String(formData.context)}
              onChange={handleChange}
              placeholder="e.g., Background research for case, policy analysis, trend investigation"
              rows={3}
              className="w-full resize-none"
            />
          </div>
        </>
      )}

      {/* Common Priority Field */}
      <div>
        <label htmlFor="priority" className="block text-sm font-medium text-contrast mb-2">
          Investigation Priority
        </label>
        <select
          id="priority"
          name="priority"
          value={String(formData.priority)}
          onChange={handleChange}
          className="w-full"
        >
          <option value="normal">Normal Priority</option>
          <option value="high">High Priority</option>
          <option value="urgent">Urgent</option>
        </select>
      </div>

      {/* Submit Button */}
      <div className="pt-4">
        <button
          type="submit"
          disabled={!isFormValid() || isLoading}
          className={`w-full btn-primary py-3 px-6 rounded-lg font-medium transition-all duration-200 ${
            !isFormValid() || isLoading
              ? 'opacity-50 cursor-not-allowed'
              : 'hover:shadow-lg'
          }`}
        >
          {isLoading ? (
            <div className="flex items-center justify-center space-x-2">
              <div className="animate-spin w-5 h-5 border-2 border-primary-foreground border-t-transparent rounded-full"></div>
              <span>Investigating...</span>
            </div>
          ) : (
            `Start ${investigationTypes.find(t => t.value === investigationType)?.label} Investigation`
          )}
        </button>
      </div>

      {!isFormValid() && (
        <p className="text-sm text-muted-foreground text-center">
          Please fill in all required fields (marked with *) to start the investigation.
        </p>
      )}
    </form>
  );
}
