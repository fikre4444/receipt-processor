import PropTypes from 'prop-types';
import { X } from 'lucide-react';

const Modal = ({ isOpen, onClose, title, children, mode = 'data' }) => {
    if (!isOpen) return null;

    const contentClass = mode === 'image' ? 'image-mode' : 'data-mode';

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className={`modal-content ${contentClass}`} onClick={e => e.stopPropagation()}>
                {mode === 'image' ? (
                    <>
                        <button className="modal-close-btn" onClick={onClose}>
                            <X size={24} />
                        </button>
                        {children}
                    </>
                ) : (
                    <>
                        <div className="modal-header">
                            <h3>{title}</h3>
                            <button className="icon-btn" onClick={onClose}>
                                <X size={20} />
                            </button>
                        </div>
                        <div className="modal-body">
                            {children}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

Modal.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    title: PropTypes.string,
    children: PropTypes.node.isRequired,
    mode: PropTypes.oneOf(['image', 'data']),
};

export default Modal;
