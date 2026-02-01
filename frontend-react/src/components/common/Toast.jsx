import PropTypes from 'prop-types';
import { Clock } from 'lucide-react';

const Toast = ({ show, title, subtitle, icon: Icon = Clock }) => {
    if (!show) return null;

    return (
        <div className="ai-toast fade-in">
            <Icon size={16} />
            <div>
                <strong>{title}</strong>
                {subtitle && (
                    <div style={{ fontSize: '0.75rem', opacity: 0.9 }}>
                        {subtitle}
                    </div>
                )}
            </div>
        </div>
    );
};

Toast.propTypes = {
    show: PropTypes.bool.isRequired,
    title: PropTypes.string.isRequired,
    subtitle: PropTypes.string,
    icon: PropTypes.elementType,
};

export default Toast;
