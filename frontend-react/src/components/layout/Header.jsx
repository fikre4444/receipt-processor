import { Activity, AlertCircle } from 'lucide-react';
import PropTypes from 'prop-types';
import Pill from '../common/Pill';

const Header = ({ healthStatus }) => {
    return (
        <header>
            <h1>Receipt Processor</h1>
            <div className="header-meta">
                <Pill
                    type={healthStatus}
                    icon={healthStatus === 'ok' ? Activity : AlertCircle}
                    label={healthStatus === 'ok' ? 'System Online' : healthStatus === 'loading' ? 'Checking System...' : 'Offline'}
                />
            </div>
        </header>
    );
};

Header.propTypes = {
    healthStatus: PropTypes.oneOf(['ok', 'error', 'loading']).isRequired,
};

export default Header;
