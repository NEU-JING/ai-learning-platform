/**
 * ErrorBoundary - 全局错误边界组件
 * 捕获 React 组件树中任何地方的渲染错误，防止整站崩溃
 */
import React from 'react';
import { Icon } from '../icons';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null,
      errorInfo: null 
    };
  }

  static getDerivedStateFromError(error) {
    // 更新 state 使下一次渲染显示降级 UI
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // 记录错误信息
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({ errorInfo });
    
    // 可以在这里发送错误到监控服务
    // reportError(error, errorInfo);
  }

  handleRetry = () => {
    // 清除错误状态，尝试重新渲染
    this.setState({ hasError: false, error: null, errorInfo: null });
    
    // 如果是路由错误，尝试刷新页面
    if (this.props.onRetry) {
      this.props.onRetry();
    }
  };

  handleGoHome = () => {
    window.location.hash = '#/';
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      // 自定义降级 UI
      return (
        <div className="error-boundary" style={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '40px 20px',
          background: 'var(--background, #0b0c0f)',
          color: 'var(--text, #e7e9ed)',
          textAlign: 'center'
        }}>
          <div style={{
            width: 80,
            height: 80,
            borderRadius: '50%',
            background: 'rgba(251, 113, 133, 0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: 24
          }}>
            <Icon name="alert" size={40} color="#fb7185" />
          </div>
          
          <h1 style={{
            fontSize: 24,
            fontWeight: 600,
            marginBottom: 12,
            color: 'var(--text, #e7e9ed)'
          }}>
            页面出错了
          </h1>
          
          <p style={{
            fontSize: 14,
            color: 'var(--muted, #9aa3b2)',
            marginBottom: 32,
            maxWidth: 400,
            lineHeight: 1.6
          }}>
            抱歉，页面加载时遇到了问题。您可以尝试重新加载或返回首页。
          </p>

          {process.env.NODE_ENV === 'development' && this.state.error && (
            <div style={{
              background: 'rgba(0,0,0,0.3)',
              borderRadius: 8,
              padding: 16,
              marginBottom: 24,
              maxWidth: 600,
              textAlign: 'left',
              fontFamily: 'monospace',
              fontSize: 12,
              color: '#fb7185',
              overflow: 'auto',
              maxHeight: 200
            }}>
              <strong style={{ color: '#fb7185' }}>{this.state.error.toString()}</strong>
              {this.state.errorInfo?.componentStack && (
                <pre style={{ marginTop: 8, whiteSpace: 'pre-wrap' }}>
                  {this.state.errorInfo.componentStack}
                </pre>
              )}
            </div>
          )}
          
          <div style={{
            display: 'flex',
            gap: 12,
            flexWrap: 'wrap',
            justifyContent: 'center'
          }}>
            <button
              onClick={this.handleRetry}
              style={{
                padding: '10px 20px',
                borderRadius: 8,
                border: 'none',
                background: 'var(--brand, #818cf8)',
                color: '#fff',
                fontSize: 14,
                fontWeight: 500,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 8
              }}
            >
              <Icon name="refresh" size={14} />
              重新加载
            </button>
            
            <button
              onClick={this.handleGoHome}
              style={{
                padding: '10px 20px',
                borderRadius: 8,
                border: '1px solid var(--line, #23252c)',
                background: 'transparent',
                color: 'var(--text, #e7e9ed)',
                fontSize: 14,
                fontWeight: 500,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 8
              }}
            >
              <Icon name="arrowLeft" size={14} />
              返回首页
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
