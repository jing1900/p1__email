function mao(fff,t){
    if(t == 'no'){
        alert('请登录后评论')
    }

    var oExports = {
        initialize: fInitialize(fff),
        encode: fEncode
    };
    oExports.initialize();

    function fInitialize(fff) {

        //alert(image_id)
        var that = this;
        //var test = new RegExp("jsSubmit")
        var sImageId =fff;

        var oCmtIpt = $('#jsCmt'+fff);
        //var oListDv = $('ul.discuss-list-js-discuss-list'+fff);
        var oListDv = $('#ul'+fff);
        var s = 'jsSubmit' + sImageId.toString()

        // 点击添加评论
        var bSubmit = false;
        var id = sImageId;
        //alert(id)
            var sCmt = $.trim(oCmtIpt.val());
            // 评论为空不能提交
            if (!sCmt) {
                return alert('评论不能为空');
            }
            // 上一个提交没结束之前，不再提交新的评论
            if (bSubmit) {
                return;
            }
            bSubmit = true;
            $.ajax({
                url: '/addindexcomment/',
                type: 'post',
                data: {image_id: sImageId, content: sCmt}
            }).done(function (oResult) {
                oResult = eval('(' + oResult + ')')
                //alert(oResult.code)
                if (oResult.code !== 0) {

                    return alert(oResult.msg || '提交失败1，请重试');
                }
                // 清空输入框
                oCmtIpt.val('');
                // 渲染新的评论
                if (oResult.image_id == sImageId){
                    //alert(fEncode(oResult.username))
                    //alert((oResult.username))
                    var sHtml = [
                        '<li>',
                        '<a class="_4zhc5 _iqaka" title="', fEncode(oResult.username), '" href="/profile/', oResult.user_id, '">', fEncode(oResult.username), '</a> ',
                        '<span><span>', fEncode(sCmt), '</span></span>',
                        '</li>'].join('');
                    oListDv.prepend(sHtml);
                }

            }).fail(function (oResult) {
                alert(oResult.msg || '请登录后评论');
            }).always(function () {
                bSubmit = false;
            });
    }

    function fEncode(sStr, bDecode) {
        var aReplace =["&#39;", "'", "&quot;", '"', "&nbsp;", " ", "&gt;", ">", "&lt;", "<", "&amp;", "&", "&yen;", "¥"];
        !bDecode && aReplace.reverse();
        for (var i = 0, l = aReplace.length; i < l; i += 2) {
             sStr = sStr.replace(new RegExp(aReplace[i],'g'), aReplace[i+1]);
        }
        return sStr;
    };

}