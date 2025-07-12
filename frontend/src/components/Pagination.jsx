import React from 'react';

const Pagination = ({ 
  currentPage, 
  totalPages, 
  totalItems, 
  itemsPerPage, 
  onPageChange, 
  hasNext, 
  hasPrev,
  isLoading = false 
}) => {
  // Generate page numbers to show
  const getPageNumbers = () => {
    const pageNumbers = [];
    const maxPagesToShow = 5;
    
    if (totalPages <= maxPagesToShow) {
      // Show all pages if we have 5 or fewer
      for (let i = 1; i <= totalPages; i++) {
        pageNumbers.push(i);
      }
    } else {
      // Always show first page
      pageNumbers.push(1);
      
      let startPage = Math.max(2, currentPage - 1);
      let endPage = Math.min(totalPages - 1, currentPage + 1);
      
      // Add ellipsis if there's a gap after page 1
      if (startPage > 2) {
        pageNumbers.push('...');
      }
      
      // Add middle pages
      for (let i = startPage; i <= endPage; i++) {
        pageNumbers.push(i);
      }
      
      // Add ellipsis if there's a gap before last page
      if (endPage < totalPages - 1) {
        pageNumbers.push('...');
      }
      
      // Always show last page (if more than 1 page)
      if (totalPages > 1) {
        pageNumbers.push(totalPages);
      }
    }
    
    return pageNumbers;
  };

  const pageNumbers = getPageNumbers();
  const startItem = (currentPage - 1) * itemsPerPage + 1;
  const endItem = Math.min(currentPage * itemsPerPage, totalItems);

  if (totalPages <= 1) {
    return null; // Don't show pagination for single page
  }

  return (
    <div className="pagination-container">
      {/* Results info */}
      <div className="pagination-info">
        Showing {startItem}-{endItem} of {totalItems} results
      </div>

      {/* Pagination controls */}
      <div className="pagination-controls">
        {/* Previous button */}
        <button
          className={`pagination-btn ${!hasPrev || isLoading ? 'disabled' : ''}`}
          onClick={() => hasPrev && !isLoading && onPageChange(currentPage - 1)}
          disabled={!hasPrev || isLoading}
          title="Previous page"
        >
          ← Previous
        </button>

        {/* Page numbers */}
        <div className="pagination-numbers">
          {pageNumbers.map((pageNum, index) => (
            <button
              key={index}
              className={`pagination-number ${
                pageNum === currentPage ? 'active' : ''
              } ${pageNum === '...' ? 'ellipsis' : ''} ${isLoading ? 'disabled' : ''}`}
              onClick={() => {
                if (pageNum !== '...' && pageNum !== currentPage && !isLoading) {
                  onPageChange(pageNum);
                }
              }}
              disabled={pageNum === '...' || pageNum === currentPage || isLoading}
            >
              {pageNum}
            </button>
          ))}
        </div>

        {/* Next button */}
        <button
          className={`pagination-btn ${!hasNext || isLoading ? 'disabled' : ''}`}
          onClick={() => hasNext && !isLoading && onPageChange(currentPage + 1)}
          disabled={!hasNext || isLoading}
          title="Next page"
        >
          Next →
        </button>
      </div>

      {/* Page size info */}
      <div className="pagination-page-size">
        {itemsPerPage} per page
      </div>

      <style jsx>{`
        .pagination-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 12px;
          margin: 20px 0;
          padding: 16px;
          background: #f8f9fa;
          border-radius: 8px;
          border: 1px solid #e9ecef;
        }

        .pagination-info, .pagination-page-size {
          font-size: 14px;
          color: #6c757d;
          font-weight: 500;
        }

        .pagination-controls {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .pagination-numbers {
          display: flex;
          gap: 4px;
        }

        .pagination-btn, .pagination-number {
          padding: 8px 12px;
          border: 1px solid #dee2e6;
          background: white;
          color: #495057;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          transition: all 0.2s ease;
          min-width: 40px;
        }

        .pagination-btn:hover:not(.disabled),
        .pagination-number:hover:not(.disabled):not(.active):not(.ellipsis) {
          background: #e9ecef;
          border-color: #adb5bd;
        }

        .pagination-number.active {
          background: #007bff;
          border-color: #007bff;
          color: white;
          font-weight: 600;
        }

        .pagination-number.ellipsis {
          border: none;
          background: transparent;
          cursor: default;
          font-weight: bold;
        }

        .pagination-btn.disabled,
        .pagination-number.disabled {
          opacity: 0.5;
          cursor: not-allowed;
          background: #f8f9fa;
        }

        @media (max-width: 768px) {
          .pagination-container {
            padding: 12px;
          }
          
          .pagination-controls {
            flex-direction: column;
            gap: 12px;
          }
          
          .pagination-btn, .pagination-number {
            padding: 6px 10px;
            font-size: 13px;
          }
        }
      `}</style>
    </div>
  );
};

export default Pagination;
