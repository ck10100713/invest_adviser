from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def investment(request):
    return render(request, 'investment/investment.html')

def investment_controller(request):
    is_advanced_mode = True
    context = {
        'is_advanced_mode': is_advanced_mode
    }
    return render(request, 'investment/investment.html', context)


from django.http import JsonResponse

def toggle_mode(request):
    print('hi')
    if request.method == 'POST':
        mode = request.POST.get('mode')
        # 根據模式做出相應的處理，這裡只是一個示例
        if mode == 'advanced':
            is_advanced_mode = True
            # 切換到進階模式的處理代碼
            # 例如，更新用戶的設置或者處理其他邏輯
            pass
        elif mode == 'normal':
            is_advanced_mode = False
            # 切換到普通模式的處理代碼
            # 例如，更新用戶的設置或者處理其他邏輯
            pass
        # 返回成功的響應
        context = {
        'is_advanced_mode': is_advanced_mode
    }
        return render(request, 'investment/investment.html', context)
        # return JsonResponse({'status': 'success'})
    else:
        # 返回失敗的響應
        return JsonResponse({'status': 'error'})