$(function () {
    var oExports = {
        initialize: fInitialize,
        // 渲染更多数据
        renderMore: fRenderMore,
        // 请求数据
        requestData: fRequestData,
        // 简单的模板替换
        tpl: fTpl
    };
    // 初始化页面脚本
    oExports.initialize();

    function fInitialize() {
        var that = this;
        // 常用元素
        that.listEl = $('div.js-image-list');
        // 初始化数据
        that.page = 1;
        that.pageSize = 10;
        that.listHasNext = true;
        // 绑定事件
        $('.js-load-more').on('click', function (oEvent) {
            //alert('执行onclick')
            var oEl = $(oEvent.currentTarget);
            var sAttName = 'data-load';
            // 正在请求数据中，忽略点击事件
            if (oEl.attr(sAttName) === '1') {
                return;
            }
            // 增加标记，避免请求过程中的频繁点击
            oEl.attr(sAttName, '1');
            that.renderMore(function () {
                // 取消点击标记位，可以进行下一次加载
                oEl.removeAttr(sAttName);
                // 没有数据隐藏加载更多按钮
                !that.listHasNext && oEl.hide();
            });
        });
    }

    function fRenderMore(fCb) {
        //alert('执行rendermore')
        var that = this;
        // 没有更多数据，不处理
        if (!that.listHasNext) {
            return;
        }
        that.requestData({
            page: that.page + 1,
            pageSize: that.pageSize,
            call: function (oResult) {
                //alert(oResult)
                // 是否有更多数据
                that.listHasNext = !!oResult.has_next && (oResult.images || []).length > 0;
                // 更新当前页面
                that.page++;
                // 渲染数据
                var sHtml = '';
                $.each(oResult.images, function (nIndex, oImage) {
                    sHtml_1 = that.tpl([
                        '<article class="mod">',
                            '<header class="mod-hd">',
                                '<time class="time">#{created_date}</time>',
                                '<a href="/profile/#{user_id}" class="avatar">',
                                    '<img src="#{head_url}">',
                                '</a>',
                                '<div class="profile-info">',
                                    '<a title="#{imageusername}" href="/profile/#{user_id}">#{imageusername}</a>',
                                '</div>',
                            '</header>',
                            '<div class="mod-bd">',
                                '<div class="img-box">',
                                    '<a href="/image/#{id}">',
                                        '<img src="#{url}">',
                                    '</a>',
                                '</div>',
                            '</div>',
                            '<div class="mod-ft">',
                                '<ul class="discuss-list js-discuss-list" id="ul#{id}">',
                                    '<li class="more-discuss">',
                                        '<a>',
                                            '<span>全部 </span><span class="">#{comment_count}</span>',
                                            '<span> 条评论</span></a>',
                                    '</li>'].join(''), oImage);
                    //alert(sHtml_1)
                    sHtml_2 = ' ';
                    for (var ni = 0; ni < oImage.comment_count; ni++){
                        //alert(ni)
                        dict = {'comment_user_username':oImage.comment_user_username[ni], 'comment_user_id':oImage.comment_user_id[ni],
                            'comment_content':oImage.comment_content[ni] };
                        //alert(dict)
                        sHtml_2 += that.tpl([
                            '<li>',
                            '<a class="_4zhc5 _iqaka" title="#{comment_user_username}" href="/profile/#{comment_user_id}" data-reactid=".0.1.0.0.0.2.1.2:$comment-17856951190001917.1">#{comment_user_username}</a>',
                            '<span>',
                            '<span>#{comment_content}</span>',
                            '</span>',
                            '</li>'].join(''), dict);

                    }
                    //alert(sHtml_2)
                    sHtml_3 = that.tpl([
                                '</ul>',
                                '<section class="discuss-edit">',
                                    '<a class="icon-heart-empty"></a>',
                                        '<form>',
                                            '<input placeholder="添加评论..." id="jsCmt#{id}" type="text">',
                                        '</form>',
                                        '<button class="more-info" id="jsSubmit#{id}" onclick="mao(#{id})">更多选项</button>',
                                '</section>',
                            '</div>',
                        '</article>'].join(''), oImage);
                    //alert(sHtml_3)
                    sHtml += sHtml_1  +sHtml_2+ sHtml_3;
                });
                //alert(sHtml)
                sHtml && that.listEl.append(sHtml);
            },
            error: function () {
                alert('出现错误，请稍后重试');
            },
            always: fCb
        });
    }

    function fRequestData(oConf) {
        //alert('执行frequest')
        var that = this;
        var sUrl = '/index/images/' + oConf.page + '/' + oConf.pageSize + '/';
        //alert(sUrl)
        $.ajax({url: sUrl, dataType: 'json'}).done(oConf.call).fail(oConf.error).always(oConf.always);

    }

    function fTpl(sTpl, oData) {
        var that = this;
        sTpl = $.trim(sTpl);
        return sTpl.replace(/#{(.*?)}/g, function (sStr, sName) {
            return oData[sName] === undefined || oData[sName] === null ? '' : oData[sName];
        });
    }
});
