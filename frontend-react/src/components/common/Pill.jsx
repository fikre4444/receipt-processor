import PropTypes from 'prop-types';

const Pill = ({ label, icon: Icon, type = 'default', className = '' }) => {
    return (
        <span className={`health-pill ${type} ${className}`}>
            {Icon && <Icon size={12} />}
            {label}
        </span>
    );
};

Pill.propTypes = {
    label: PropTypes.string.isRequired,
    icon: PropTypes.elementType,
    type: PropTypes.oneOf(['ok', 'error', 'loading', 'default']),
    className: PropTypes.string,
};

export default Pill;
