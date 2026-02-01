import PropTypes from 'prop-types';
import { Cpu, ShieldAlert, ChevronRight } from 'lucide-react';
import { getTagStyle, formatCurrency } from '../../utils/helpers';

const ResultView = ({ data }) => {
    if (!data) return null;

    const hasBreakdown = data.subtotal || data.tax || data.tip || data.discount || data.other_fees;

    return (
        <div className="result-container fade-in">
            <div className="merchant-header">
                <div className="merchant-label">Merchant</div>
                <div className="merchant-name">{data.merchant || "Unknown Merchant"}</div>
            </div>

            <div className="grid">
                <div className="stat">
                    <span>Grand Total</span>
                    <strong className="total-main">{formatCurrency(data.total)}</strong>
                </div>
                <div className="stat">
                    <span>Date Extracted</span>
                    <strong>{data.date || 'N/A'}</strong>
                </div>
            </div>

            {hasBreakdown && (
                <div className="breakdown-section">
                    <div className="section-title">Financial Breakdown</div>
                    <div className="breakdown-list">
                        {data.subtotal > 0 && (
                            <div className="breakdown-row">
                                <span>Subtotal</span>
                                <span>{formatCurrency(data.subtotal)}</span>
                            </div>
                        )}
                        {data.tax > 0 && (
                            <div className="breakdown-row">
                                <span>Tax / VAT</span>
                                <span>+ {formatCurrency(data.tax)}</span>
                            </div>
                        )}
                        {data.tip > 0 && (
                            <div className="breakdown-row highlight-blue">
                                <span>Tip / Service Charge</span>
                                <span>+ {formatCurrency(data.tip)}</span>
                            </div>
                        )}
                        {data.discount > 0 && (
                            <div className="breakdown-row highlight-green">
                                <span>Discount / Savings</span>
                                <span>- {formatCurrency(data.discount)}</span>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {data.summary && (
                <div className="summary-box">
                    <div className="summary-header">
                        <Cpu size={16} /> AI Analysis
                    </div>
                    <div className="summary-text">{data.summary}</div>
                </div>
            )}

            {data.tags?.length > 0 && (
                <div className="tags-section">
                    <div className="tags-header">
                        <ShieldAlert size={14} /> Audit Flags
                    </div>
                    <div className="tags-list">
                        {data.tags.map(t => {
                            const style = getTagStyle(t);
                            return (
                                <span
                                    key={t}
                                    className="tag"
                                    style={{ ...style, border: `1px solid ${style.border}` }}
                                >
                                    {t.replace(/_/g, ' ')}
                                </span>
                            );
                        })}
                    </div>
                </div>
            )}

            <details className="raw-ocr-details">
                <summary>
                    View Raw OCR Text <ChevronRight size={14} className="chevron" />
                </summary>
                <pre>{data.raw_text}</pre>
            </details>
        </div>
    );
};

ResultView.propTypes = {
    data: PropTypes.shape({
        merchant: PropTypes.string,
        total: PropTypes.number,
        date: PropTypes.string,
        subtotal: PropTypes.number,
        tax: PropTypes.number,
        tip: PropTypes.number,
        discount: PropTypes.number,
        other_fees: PropTypes.number,
        summary: PropTypes.string,
        tags: PropTypes.arrayOf(PropTypes.string),
        raw_text: PropTypes.string,
    }),
};

export default ResultView;
