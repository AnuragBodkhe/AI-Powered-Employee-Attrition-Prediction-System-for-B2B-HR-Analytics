// Reusable Component Templates for Modern Minimalist UI
// Copy and adapt these templates for your projects

// ============================================
// 1. BUTTON COMPONENT
// ============================================

import React from 'react';

const Button = ({ 
  variant = 'primary', 
  size = 'md', 
  disabled = false, 
  loading = false, 
  icon: Icon,
  children, 
  ...props 
}) => {
  const baseClasses = 'inline-flex items-center justify-center gap-2 font-medium transition-all duration-200 focus-ring';
  
  const variantClasses = {
    primary: 'bg-primary-600 text-neutral-0 hover:bg-primary-700 shadow-sm hover:shadow-md active:bg-primary-800',
    secondary: 'bg-neutral-100 text-neutral-900 border border-neutral-200 hover:bg-neutral-150 hover:border-neutral-300',
    ghost: 'text-primary-600 hover:bg-primary-50 border border-primary-200',
    danger: 'bg-error text-neutral-0 hover:bg-red-700 active:bg-red-800',
  };

  const sizeClasses = {
    sm: 'px-3 py-2 text-sm rounded-md',
    md: 'px-4 py-2.5 text-base rounded-lg',
    lg: 'px-6 py-3 text-lg rounded-lg',
  };

  return (
    <button
      disabled={disabled || loading}
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} disabled:opacity-50 disabled:cursor-not-allowed`}
      {...props}
    >
      {loading && <span className="animate-spin">⟳</span>}
      {Icon && <Icon size={20} />}
      {children}
    </button>
  );
};

export default Button;


// ============================================
// 2. CARD COMPONENT
// ============================================

const Card = ({ 
  elevated = false, 
  hover = true, 
  children, 
  className = '',
  ...props 
}) => {
  return (
    <div
      className={`
        bg-neutral-0 border border-neutral-200 rounded-xl p-6
        transition-all duration-300
        ${hover && 'hover:shadow-md hover:border-neutral-300'}
        ${elevated && 'shadow-lg'}
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;


// ============================================
// 3. INPUT FIELD COMPONENT
// ============================================

const Input = React.forwardRef(({ 
  label, 
  error, 
  helpText, 
  icon: Icon,
  ...props 
}, ref) => {
  return (
    <div className="space-y-1.5">
      {label && (
        <label className="block text-sm font-medium text-neutral-900">
          {label}
          {props.required && <span className="text-error ml-1">*</span>}
        </label>
      )}
      
      <div className="relative">
        {Icon && (
          <Icon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-500" />
        )}
        
        <input
          ref={ref}
          className={`
            w-full px-4 py-2.5 ${Icon ? 'pl-10' : ''} 
            border rounded-lg font-400 transition-all duration-200
            placeholder-neutral-500 text-neutral-900
            ${error 
              ? 'border-error focus:border-error focus:ring-1 focus:ring-error/20 focus:bg-neutral-0' 
              : 'border-neutral-200 focus:border-primary-500 focus:ring-1 focus:ring-primary-500/20 focus:bg-neutral-0'
            }
            disabled:bg-neutral-50 disabled:text-neutral-500 disabled:cursor-not-allowed
          `}
          {...props}
        />
      </div>

      {error && (
        <p className="text-xs text-error">{error}</p>
      )}
      {helpText && !error && (
        <p className="text-xs text-neutral-600">{helpText}</p>
      )}
    </div>
  );
});

Input.displayName = 'Input';
export default Input;


// ============================================
// 4. SELECT COMPONENT
// ============================================

const Select = React.forwardRef(({ 
  label, 
  options = [], 
  error,
  ...props 
}, ref) => {
  return (
    <div className="space-y-1.5">
      {label && (
        <label className="block text-sm font-medium text-neutral-900">
          {label}
        </label>
      )}
      
      <select
        ref={ref}
        className={`
          w-full px-4 py-2.5 rounded-lg border font-400 transition-all duration-200
          text-neutral-900 bg-neutral-0 cursor-pointer
          ${error 
            ? 'border-error focus:border-error focus:ring-1 focus:ring-error/20' 
            : 'border-neutral-200 focus:border-primary-500 focus:ring-1 focus:ring-primary-500/20'
          }
          disabled:bg-neutral-50 disabled:text-neutral-500 disabled:cursor-not-allowed
        `}
        {...props}
      >
        {options.map(opt => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      
      {error && (
        <p className="text-xs text-error">{error}</p>
      )}
    </div>
  );
});

Select.displayName = 'Select';
export default Select;


// ============================================
// 5. ALERT COMPONENT
// ============================================

const Alert = ({ 
  type = 'info', // success, warning, error, info
  title,
  message,
  onClose,
  icon: Icon,
  actionButton,
  className = '',
}) => {
  const typeClasses = {
    success: 'bg-emerald-50 border-emerald-200 text-emerald-900',
    warning: 'bg-amber-50 border-amber-200 text-amber-900',
    error: 'bg-red-50 border-red-200 text-red-900',
    info: 'bg-primary-50 border-primary-200 text-primary-900',
  };

  return (
    <div className={`
      border rounded-lg p-4 animate-slide-up
      flex gap-3 items-start
      ${typeClasses[type]}
      ${className}
    `}>
      {Icon && <Icon className="w-5 h-5 flex-shrink-0 mt-0.5" />}
      
      <div className="flex-1">
        {title && <h4 className="font-semibold text-sm">{title}</h4>}
        {message && <p className="text-sm mt-1">{message}</p>}
      </div>

      <div className="flex gap-2 items-center">
        {actionButton && (
          <button className={`text-sm font-medium px-3 py-1 rounded hover:opacity-80 transition-opacity`}>
            {actionButton.label}
          </button>
        )}
        {onClose && (
          <button onClick={onClose} className="text-lg leading-none hover:opacity-60 transition-opacity">
            ×
          </button>
        )}
      </div>
    </div>
  );
};

export default Alert;


// ============================================
// 6. BADGE COMPONENT
// ============================================

const Badge = ({ 
  variant = 'neutral', 
  children,
  icon: Icon,
  className = '',
}) => {
  const variantClasses = {
    neutral: 'bg-neutral-100 text-neutral-800 border-neutral-200',
    primary: 'bg-primary-100 text-primary-800 border-primary-200',
    success: 'bg-emerald-100 text-emerald-800 border-emerald-200',
    warning: 'bg-amber-100 text-amber-800 border-amber-200',
    error: 'bg-red-100 text-red-800 border-red-200',
  };

  return (
    <span className={`
      inline-flex items-center gap-1 px-2.5 py-1 rounded-full
      text-xs font-medium border
      ${variantClasses[variant]}
      ${className}
    `}>
      {Icon && <Icon size={14} />}
      {children}
    </span>
  );
};

export default Badge;


// ============================================
// 7. LOADING SPINNER COMPONENT
// ============================================

const Spinner = ({ 
  size = 'md', 
  label,
  className = '',
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  return (
    <div className={`flex flex-col items-center gap-3 ${className}`}>
      <div className={`${sizeClasses[size]} animate-spin`}>
        <svg 
          className="w-full h-full text-primary-600" 
          fill="none" 
          viewBox="0 0 24 24"
        >
          <circle 
            className="opacity-25" 
            cx="12" 
            cy="12" 
            r="10" 
            stroke="currentColor" 
            strokeWidth="4"
          />
          <path 
            className="opacity-75" 
            fill="currentColor" 
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      </div>
      {label && <p className="text-sm text-neutral-600">{label}</p>}
    </div>
  );
};

export default Spinner;


// ============================================
// 8. MODAL/DIALOG COMPONENT
// ============================================

const Modal = ({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  footer,
  size = 'md',
}) => {
  const sizeClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    full: 'max-w-4xl',
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-neutral-900/20 backdrop-blur-sm z-40"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-scale-in">
        <div className={`bg-neutral-0 rounded-xl shadow-xl ${sizeClasses[size]} overflow-hidden`}>
          {/* Header */}
          {title && (
            <div className="border-b border-neutral-200 p-6">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-neutral-900">{title}</h2>
                <button 
                  onClick={onClose}
                  className="text-neutral-500 hover:text-neutral-700 text-2xl leading-none"
                >
                  ×
                </button>
              </div>
            </div>
          )}

          {/* Body */}
          <div className="p-6">
            {children}
          </div>

          {/* Footer */}
          {footer && (
            <div className="border-t border-neutral-200 p-6 bg-neutral-50">
              <div className="flex gap-3 justify-end">
                {footer}
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default Modal;


// ============================================
// 9. TABLE COMPONENT
// ============================================

const Table = ({ 
  columns, 
  data, 
  striped = true,
  hoverable = true,
  loading = false,
}) => {
  if (loading) {
    return (
      <div className="flex justify-center items-center h-48">
        <Spinner label="Loading..." />
      </div>
    );
  }

  return (
    <div className="overflow-x-auto border border-neutral-200 rounded-lg">
      <table className="w-full">
        <thead className="bg-neutral-50 border-b border-neutral-200">
          <tr>
            {columns.map(col => (
              <th 
                key={col.key}
                className="px-6 py-3 text-left text-sm font-semibold text-neutral-900"
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr 
              key={idx}
              className={`
                border-b border-neutral-200
                ${striped && idx % 2 === 1 ? 'bg-neutral-50' : 'bg-neutral-0'}
                ${hoverable && 'hover:bg-neutral-100 transition-colors'}
              `}
            >
              {columns.map(col => (
                <td 
                  key={col.key}
                  className="px-6 py-4 text-sm text-neutral-700"
                >
                  {col.render ? col.render(row[col.key], row) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Table;


// ============================================
// 10. EMPTY STATE COMPONENT
// ============================================

const EmptyState = ({ 
  icon: Icon,
  title,
  description,
  action,
  imageUrl,
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      {imageUrl ? (
        <img src={imageUrl} alt="Empty" className="w-32 h-32 mb-4 opacity-50" />
      ) : Icon ? (
        <div className="w-16 h-16 rounded-full bg-neutral-100 flex items-center justify-center mb-4">
          <Icon className="w-8 h-8 text-neutral-400" />
        </div>
      ) : null}
      
      <h3 className="text-lg font-semibold text-neutral-900 mb-2">{title}</h3>
      <p className="text-neutral-600 text-center max-w-sm mb-6">{description}</p>
      
      {action && (
        <button className="btn-primary">
          {action.label}
        </button>
      )}
    </div>
  );
};

export default EmptyState;


// ============================================
// USAGE EXAMPLES
// ============================================

/*

// Example 1: Simple Form
<div className="space-y-4">
  <Input 
    label="Email" 
    type="email" 
    required
    placeholder="you@example.com"
  />
  <Button variant="primary">
    Submit
  </Button>
</div>

// Example 2: Dashboard Card
<Card>
  <h3 className="text-lg font-semibold mb-4">Metrics</h3>
  <Table columns={columns} data={data} />
</Card>

// Example 3: Alert with Action
<Alert 
  type="warning"
  title="Action Required"
  message="Please review these items"
  onClose={() => setShowAlert(false)}
  actionButton={{ label: 'Review' }}
/>

// Example 4: Modal with Form
<Modal 
  isOpen={showModal}
  onClose={() => setShowModal(false)}
  title="Create New Item"
  footer={<>
    <Button variant="secondary" onClick={() => setShowModal(false)}>Cancel</Button>
    <Button variant="primary">Create</Button>
  </>}
>
  <Input label="Name" required />
</Modal>

*/
