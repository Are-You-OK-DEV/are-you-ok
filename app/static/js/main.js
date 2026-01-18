// 通用工具函数
$(document).ready(function() {
    // 自动隐藏警报消息
    $('.alert').each(function() {
        const $alert = $(this);
        setTimeout(function() {
            $alert.fadeOut('slow', function() {
                $(this).remove();
            });
        }, 5000);
    });

    // 确认删除
    $('.confirm-delete').on('click', function(e) {
        if (!confirm('确定要删除吗？')) {
            e.preventDefault();
        }
    });

    // 导航栏活跃状态
    const currentLocation = location.pathname;
    $('.navbar-nav a').each(function() {
        const href = $(this).attr('href');
        if (currentLocation.includes(href) && href !== '/') {
            $(this).addClass('active');
        }
    });

    // 文本计数器
    $('.char-counter').on('input', function() {
        const max = $(this).attr('maxlength');
        const current = $(this).val().length;
        $(this).next('.char-count').text(current + '/' + max);
    });

    // 加载状态
    $('form').on('submit', function() {
        const $btn = $(this).find('button[type="submit"]');
        $btn.prop('disabled', true).html('<span class="loading"></span> 处理中...');
    });
});

// API 调用函数
function apiCall(url, method = 'GET', data = null) {
    return $.ajax({
        url: url,
        type: method,
        data: JSON.stringify(data),
        contentType: 'application/json',
        error: function() {
            alert('请求失败，请重试');
        }
    });
}

// 格式化日期
function formatDate(date) {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// 显示通知
function showNotification(message, type = 'success') {
    const alertHtml = `
        <div class="alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    $('.container').prepend(alertHtml);
}
