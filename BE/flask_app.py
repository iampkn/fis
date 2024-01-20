# from flask import Flask, jsonify, request, abort
import pandas as pd
import pandas as pd
import requests
from datetime import datetime

# app = Flask(__name__)


# CONSTANT
oneYearRatio = 0.3
threeYearRatio = 0.4
fiveYearRatio = 0.3

YEAR_ONE = 0
YEAR_THREE = 2
YEAR_FIVE = 4

# @app.route("/")
# def hello():
#     return "Hello, World!"

def cal_growth_rate(series):
    before = series.shift(-4).values
    after = series.values
    return (after - before)/before

def calculate_point_item(chiso, tham_chieu):
    val1 = oneYearRatio if chiso[YEAR_ONE] >= tham_chieu else chiso[YEAR_ONE] / tham_chieu * oneYearRatio
    val2 = threeYearRatio if chiso[YEAR_THREE] >= tham_chieu else chiso[YEAR_THREE] / tham_chieu * threeYearRatio
    val3 = fiveYearRatio if chiso[YEAR_FIVE] >= tham_chieu else chiso[YEAR_FIVE] / tham_chieu * fiveYearRatio
    sum_val =  (val1 + val2 + val3) * 100
    if sum_val < 0: return 0
    return sum_val

def calculate4M(_STOCK):
    headers = {
        'authority': 'fwtapi2.fialda.com',
        'method': 'GET',
        'scheme' : 'https',
        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding' : 'gzip, deflate, br',
        'Accept-Language' : 'en-US,en;q=0.9',
        'Cache-Control' : 'max-age=0',
        'Sec-Ch-Ua' : '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
        'Sec-Ch-Ua-Mobile' : '?0',
        'Sec-Ch-Ua-Platform' : '"Windows"',
        'Sec-Fetch-Dest' : 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site' : 'None',
        'Sec-Fetch-User' : '?1',
        'Upgrade-Insecure-Requests' : '1',
        'User-Agent' : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    }
    api_url = f"https://fwtapi2.fialda.com/api/services/app/TechnicalAnalysis/GetFinancialHighlights?symbol={_STOCK}"

    response = requests.get(api_url,headers=headers)

    # Kiểm tra xem có lỗi không (status code 200 là thành công)
    if response.status_code == 200:
        # In nội dung phản hồi
        response = response.json()["result"]
    else:
        # In lỗi nếu có
        print(f"Lỗi {response.status_code}: {response.text}")

    response_lenght = len(response)
    df_api = pd.DataFrame()
    for i in range(response_lenght):
        df_api = pd.concat([df_api, pd.DataFrame([response[i]])])

    df_api = df_api[df_api["quarter"] != 5]
    df_api = df_api[::-1]

    current_year = datetime.now().year
    lastyear = current_year - 1

    temp = df_api[["year", "quarter", "profit"]]
    last_year_profit = temp[temp["year"] == lastyear].sum().profit

    THAM_CHIEU_SALEGR = 0.2
    TY_TRONG_SALEGR = 0.15

    THAM_CHIEU_EPS = 0.2
    TY_TRONG_EPS = 0.2

    THAM_CHIEU_BVPS = 0.15
    TY_TRONG_BVPS = 0.05

    THAM_CHIEU_OPC = 0.15
    TY_TRONG_OPC = 0.15

    THAM_CHIEU_NO_DAI_HAN = last_year_profit * 3
    TY_TRONG_NO_DAI_HAN = 0.1

    THAM_CHIEU_EFFECTIVENESS = 0.1
    TY_TRONG_EFFECTIVENESS = 0.05

    THAM_CHIEU_EFFICIENCY = 0.1
    TY_TRONG_EFFICIENCY = 0.05

    THAM_CHIEU_PRODUCTIVITY = 0.1
    TY_TRONG_PRODUCTIVITY = 0.05

    THAM_CHIEU_ROA = 0.15
    TY_TRONG_ROA = 0.1

    THAM_CHIEU_ROE = 0.2
    TY_TRONG_ROE = 0.05

    THAM_CHIEU_ROIC = 0.15
    TY_TRONG_ROIC = 0.15

    # NECESSARY
    df_api["TOTAL_ASSETS"] = df_api["marketcap"] * df_api["pb"]
    df_api["VON_CHU_SO_HUU"] = df_api["profit"] / df_api["mE_ROE"]


    # 1.Sale Growth Rate
    Sale = df_api["netSale"]
    SaleGR = cal_growth_rate(Sale)

    # 2. EPS Growth Rate
    eps = df_api["eps"]
    epsGR = cal_growth_rate(eps)

    # 3. BVPS Growht Rate
    eps = df_api["eps"]
    socp = df_api["profit"] * 1.0 /eps
    bvps = df_api["VON_CHU_SO_HUU"] / socp

    bvpsGR = cal_growth_rate(bvps)

    # 4.OPC LCDTKD
    OPC_LCDTKD = df_api["cF_Operating"]
    OPC_LCDTKDGR = cal_growth_rate(OPC_LCDTKD)

    # 5. Nợ dài hạn
    df_api["NO_DAI_HAN"] = df_api["fS_DebtOnEquityRatio"] * df_api["VON_CHU_SO_HUU"]
    temp = df_api[["year", "quarter", "NO_DAI_HAN"]]
    no_dai_han = temp[temp["year"] == lastyear].sum().NO_DAI_HAN
    no_dai_han

    # 6. Effectiveness
    effectiveness = df_api["netSale"] / df_api["TOTAL_ASSETS"]
    effectivenessGR = cal_growth_rate(effectiveness)

    # 7. Efficiency
    efficiency = df_api["profit"] / df_api["netSale"]
    efficiencyGR = cal_growth_rate(efficiency)

    # 8.productivity
    productivity = OPC_LCDTKD / df_api["profit"]
    productivityGR = cal_growth_rate(productivity)

    # 9. ROA
    ROA = df_api["mE_ROA"]
    ROAGR = cal_growth_rate(ROA)

    # 10. ROE
    ROE = df_api["mE_ROE"]
    ROEGR = cal_growth_rate(ROE)

    # 11. ROIC
    ROIC = df_api["profit"] / (df_api["TOTAL_ASSETS"] + no_dai_han)
    ROIC_GR = cal_growth_rate(ROIC)

    sum1 = calculate_point_item(SaleGR, THAM_CHIEU_SALEGR)
    sum2 = calculate_point_item(epsGR, THAM_CHIEU_EPS)
    sum3 = calculate_point_item(bvpsGR, THAM_CHIEU_BVPS)
    sum4 = calculate_point_item(OPC_LCDTKDGR, THAM_CHIEU_OPC)
    sum5 = oneYearRatio if no_dai_han >= THAM_CHIEU_NO_DAI_HAN else no_dai_han / THAM_CHIEU_NO_DAI_HAN * oneYearRatio
    sum6 = calculate_point_item(effectivenessGR, THAM_CHIEU_EFFECTIVENESS)
    sum7 = calculate_point_item(efficiencyGR, THAM_CHIEU_EFFICIENCY)
    sum8 = calculate_point_item(productivityGR, THAM_CHIEU_PRODUCTIVITY)
    sum9 = calculate_point_item(ROAGR, THAM_CHIEU_ROA)
    sum10 = calculate_point_item(ROEGR,THAM_CHIEU_ROE)
    sum11 = calculate_point_item(ROIC_GR, THAM_CHIEU_ROIC)

    sum12 = (sum6 + sum7 + sum8)

    return sum1 * TY_TRONG_SALEGR + sum2 * TY_TRONG_EPS + sum3 * TY_TRONG_BVPS + sum4 * TY_TRONG_OPC + sum5 * TY_TRONG_NO_DAI_HAN + sum12 * TY_TRONG_EFFECTIVENESS + sum9 * TY_TRONG_ROA + sum10 * TY_TRONG_ROE + sum11 * TY_TRONG_ROIC


if __name__ == "__main__":
    # app.run(debug=True)
    print(calculate4M("BSR"))
    print(calculate4M("HUT"))
