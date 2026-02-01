import { FileDigit, Layers, Clock } from 'lucide-react';
import PropTypes from 'prop-types';

const ModeSwitcher = ({ currentMode, setMode }) => {
    const modes = [
        { id: 'single', label: 'Single Receipt', icon: FileDigit },
        { id: 'bulk', label: 'Batch Processing', icon: Layers },
        { id: 'history', label: 'History', icon: Clock },
    ];

    return (
        <div className="mode-switcher">
            {modes.map(({ id, label, icon: Icon }) => (
                <div
                    key={id}
                    className={`mode-option ${currentMode === id ? 'active' : ''}`}
                    onClick={() => setMode(id)}
                >
                    <Icon size={16} /> {label}
                </div>
            ))}
        </div>
    );
};

ModeSwitcher.propTypes = {
    currentMode: PropTypes.string.isRequired,
    setMode: PropTypes.func.isRequired,
};

export default ModeSwitcher;
