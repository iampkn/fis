from flask import Flask, jsonify, request, abort
import pandas as pd
import requests
from datetime import datetime

app = Flask(__name__)


# CONSTANT
oneYearRatio = 0.3
threeYearRatio = 0.4
fiveYearRatio = 0.3

YEAR_ONE = 0
YEAR_THREE = 2
YEAR_FIVE = 4

# define header for request
headers = {
        "authority": "fwtapi2.fialda.com",
        "method": "GET",
        "scheme": "https",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "None",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    }


@app.route("/")
def hello():
    return "Hello, World!"


def cal_growth_rate(series):
    before = series.shift(-4).values
    after = series.values
    return (after - before) / before


def calculate_point_item(chiso, tham_chieu):
    val1 = (
        oneYearRatio
        if chiso[YEAR_ONE] >= tham_chieu
        else chiso[YEAR_ONE] / tham_chieu * oneYearRatio
    )
    val2 = (
        threeYearRatio
        if chiso[YEAR_THREE] >= tham_chieu
        else chiso[YEAR_THREE] / tham_chieu * threeYearRatio
    )
    val3 = (
        fiveYearRatio
        if chiso[YEAR_FIVE] >= tham_chieu
        else chiso[YEAR_FIVE] / tham_chieu * fiveYearRatio
    )
    sum_val = (val1 + val2 + val3) * 100
    if sum_val < 0:
        return 0
    return sum_val

def handle_map_response_to_df(api_url, headers):
    response = requests.get(api_url, headers=headers)
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
    return df_api, response

def calculate4M(_STOCK):
    api_url = f"https://fwtapi2.fialda.com/api/services/app/TechnicalAnalysis/GetFinancialHighlights?symbol={_STOCK}"

    df_api, response = handle_map_response_to_df(api_url, headers)

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
    socp = df_api["profit"] * 1.0 / eps
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
    sum5 = (
        oneYearRatio
        if no_dai_han >= THAM_CHIEU_NO_DAI_HAN
        else no_dai_han / THAM_CHIEU_NO_DAI_HAN * oneYearRatio
    )
    sum6 = calculate_point_item(effectivenessGR, THAM_CHIEU_EFFECTIVENESS)
    sum7 = calculate_point_item(efficiencyGR, THAM_CHIEU_EFFICIENCY)
    sum8 = calculate_point_item(productivityGR, THAM_CHIEU_PRODUCTIVITY)
    sum9 = calculate_point_item(ROAGR, THAM_CHIEU_ROA)
    sum10 = calculate_point_item(ROEGR, THAM_CHIEU_ROE)
    sum11 = calculate_point_item(ROIC_GR, THAM_CHIEU_ROIC)

    sum12 = sum6 + sum7 + sum8

    return (
        sum1 * TY_TRONG_SALEGR
        + sum2 * TY_TRONG_EPS
        + sum3 * TY_TRONG_BVPS
        + sum4 * TY_TRONG_OPC
        + sum5 * TY_TRONG_NO_DAI_HAN
        + sum12 * TY_TRONG_EFFECTIVENESS
        + sum9 * TY_TRONG_ROA
        + sum10 * TY_TRONG_ROE
        + sum11 * TY_TRONG_ROIC
    )

def canslim(_STOCK):
    api_url = f"https://fwtapi2.fialda.com/api/services/app/TechnicalAnalysis/GetFinancialHighlights?symbol={_STOCK}"

    df_api, response = handle_map_response_to_df(api_url, headers)

    df_api = df_api[df_api["quarter"] != 5]
    df_api = df_api[::-1]
    
    df_api = df_api[["year", "quarter", "netSale", "eps"]].iloc[:9]

    THAM_CHIEU_25 = 0.25
    THAM_CHIEU_20 = 0.2
    TY_TRONG_15 = 0.15
    TY_TRONG_20 = 0.2
    TY_TRONG_10 = 0.1
    TY_TRONG_5 = 0.05
    data_sales = df_api["netSale"].values

    tltt_a_sale =  (data_sales[0] - data_sales[4])/data_sales[4]
    score_a_sale = TY_TRONG_15 if tltt_a_sale > THAM_CHIEU_25 else tltt_a_sale/THAM_CHIEU_25 * TY_TRONG_15
    score_a_sale = score_a_sale if score_a_sale > 0 else 0

    tltt_b_sale =  (data_sales[1] - data_sales[5])/data_sales[5]
    score_b_sale = TY_TRONG_10 if tltt_b_sale > THAM_CHIEU_25 else tltt_b_sale/THAM_CHIEU_25 * TY_TRONG_10
    score_b_sale = score_b_sale if score_b_sale > 0 else 0

    tltt_c_sale = (data_sales[:4].sum() - data_sales[4:4+4].sum()) /data_sales[4:4+4].sum()
    score_c_sale = TY_TRONG_10 if tltt_c_sale > THAM_CHIEU_20 else tltt_c_sale/THAM_CHIEU_20 * TY_TRONG_10
    score_c_sale = score_c_sale if score_c_sale > 0 else 0

    tltt_d_sale = (data_sales[1:5].sum() - data_sales[5:5+4].sum()) /data_sales[5:5+4].sum()
    score_d_sale = TY_TRONG_5 if tltt_d_sale > THAM_CHIEU_20 else tltt_d_sale/THAM_CHIEU_20 * TY_TRONG_5
    score_d_sale = score_d_sale if score_d_sale > 0 else 0

    data_eps = df_api["eps"].values
    tltt_a_eps =  (data_eps[0] - data_eps[4])/data_eps[4]
    score_a_eps = TY_TRONG_20 if tltt_a_eps > THAM_CHIEU_25 else tltt_a_eps/THAM_CHIEU_25 * TY_TRONG_20
    score_a_eps = score_a_eps if score_a_eps > 0 else 0

    tltt_b_eps =  (data_eps[1] - data_eps[5])/data_eps[5]
    score_b_eps = TY_TRONG_15 if tltt_b_eps > THAM_CHIEU_25 else tltt_b_eps/THAM_CHIEU_25 * TY_TRONG_15
    score_b_eps = score_b_eps if score_b_eps > 0 else 0

    tltt_c_eps = (data_eps[:4].sum() - data_eps[4:4+4].sum()) /data_eps[5:5+4].sum()
    score_c_eps = TY_TRONG_15 if tltt_c_eps > THAM_CHIEU_20 else tltt_c_eps/THAM_CHIEU_20 * TY_TRONG_15
    score_c_eps = score_c_eps if score_c_eps > 0 else 0

    tltt_d_eps = (data_eps[1:5].sum() - data_eps[5:5+4].sum()) /data_eps[5:5+4].sum()
    score_d_eps = TY_TRONG_10 if tltt_d_eps > THAM_CHIEU_20 else tltt_d_eps/THAM_CHIEU_20 * TY_TRONG_10
    score_d_eps = score_d_eps if score_d_eps > 0 else 0

    C =  score_a_eps + score_b_eps + score_a_sale + score_b_sale
    A = score_c_eps + score_d_eps + score_c_sale + score_d_sale
    
    return (C + A) * 100


def getStockName(_STOCK):
    stock_data = pd.read_excel("../stock_data/stock_info.xlsx")
    return stock_data[stock_data["StockID"] == _STOCK].StockName.values[0]


def getStockPrice(_STOCK):
    api_url = f"https://fwtapi1.fialda.com/api/services/app/StockInfo/GetTradingChartData?symbol={_STOCK}&interval=1d&toTime=2024-01-07T15:00:00.000"
    response = requests.get(api_url,headers=headers)
    if response.status_code == 200: response = response.json()["result"]
    else: print(f"Lỗi {response.status_code}: {response.text}")
    return response[0]

def getKQKD(_STOCK, isQuarterReport):
    api_url = f"https://fwtapi1.fialda.com/api/services/app/StockInfo/GetFS_IncomeStatement_General?symbol={_STOCK}&isQuarterReport={isQuarterReport}"

    df_api, response = handle_map_response_to_df(api_url, headers)

    mapping = [{"Code": "ISA1","Name": "Tổng doanh thu hoạt động kinh doanh"},{"Code": "ISA2","Name": "Các khoản giảm trừ doanh thu"},{"Code": "ISA3","Name": "Doanh thu thuần"},{"Code": "ISA4","Name": "Giá vốn hàng bán"},{"Code": "ISA5","Name": "Lợi nhuận gộp"},{"Code": "ISA6","Name": "Doanh thu hoạt động tài chính"},{"Code": "ISA7","Name": "Chi phí tài chính"},{"Code": "ISA8","Name": "Trong đó: Chi phí lãi vay"},{"Code": "ISA102","Name": "Lợi nhuận hoặc lỗ trong công ty liên kết"},{"Code": "ISA9","Name": "Chi phí bán hàng"},{"Code": "ISA10","Name": "Chi phí quản lý doanh nghiệp"},{"Code": "ISA11","Name": "Lợi nhuận thuần từ hoạt động kinh doanh"},{"Code": "ISA12","Name": "Thu nhập khác"},{"Code": "ISA13","Name": "Chi phí khác"},{"Code": "ISA14","Name": "Lợi nhuận khác"},{"Code": "ISA16","Name": "Tổng lợi nhuận kế toán trước thuế"},{"Code": "ISA19","Name": "Chi phí thuế TNDN"},{"Code": "ISA17","Name": "Chi phí thuế TNDN hiện hành"},{"Code": "ISA18","Name": "Chi phí thuế TNDN hoãn lại"},{"Code": "ISA20","Name": "Lợi nhuận sau thuế thu nhập doanh nghiệp"},{"Code": "ISA21","Name": "Lợi ích của cổ đông thiểu số"},{"Code": "ISA22","Name": "Lợi nhuận sau thuế của Công ty mẹ"},{"Code": "ISAV1","Name": "Lãi cơ bản trên cổ phiếu"},{"Code": "ISAV2","Name": "Lãi suy giảm trên cổ phiếu"}]
    df_api.columns = df_api.columns.str.upper()

    for i in range(len(mapping)):
        df_api.rename(columns={mapping[i]["Code"]: mapping[i]["Name"]},inplace=True)
    return df_api[0].to_json()

def getCDKT(_STOCK, isQuarterReport):
    api_url = f"https://fwtapi1.fialda.com/api/services/app/StockInfo/GetFS_BalanceSheet_General?symbol={_STOCK}&isQuarterReport={isQuarterReport}"

    df_api, response = handle_map_response_to_df(api_url, headers)

    mapping = [{"Code": "BSA1","Name": "Tài sản ngắn hạn"},{"Code": "BSA2","Name": "Tiền và các khoản tương đương tiền"},{"Code": "BSA3","Name": "Tiền"},{"Code": "BSA4","Name": "Các khoản tương đương tiền"},{"Code": "BSA5","Name": "Các khoản đầu tư tài chính ngắn hạn"},{"Code": "BSA6","Name": "Đầu tư ngắn hạn"},{"Code": "BSA7","Name": "Dự phòng giảm giá đầu tư ngắn hạn"},{"Code": "BSB108","Name": "Đầu tư giữ đến ngày đáo hạn"},{"Code": "BSA8","Name": "Các khoản phải thu ngắn hạn"},{"Code": "BSA9","Name": "Phải thu khách hàng"},{"Code": "BSA10","Name": "Trả trước cho người bán"},{"Code": "BSA11","Name": "Phải thu nội bộ ngắn hạn"},{"Code": "BSA12","Name": "Phải thu theo tiến độ kế hoạch hợp đồng xây dựng"},{"Code": "BSA159","Name": "Phải thu về cho vay ngắn hạn"},{"Code": "BSA13","Name": "Các khoản phải thu khác"},{"Code": "BSA14","Name": "Dự phòng phải thu ngắn hạn khó đòi"},{"Code": "BSI141","Name": "Tài sản thiếu chờ xử lý"},{"Code": "BSA15","Name": "Hàng tồn kho"},{"Code": "BSA16","Name": "Hàng tồn kho"},{"Code": "BSA17","Name": "Dự phòng giảm giá hàng tồn kho"},{"Code": "BSA18","Name": "Tài sản ngắn hạn khác"},{"Code": "BSA19","Name": "Chi phí trả trước ngắn hạn"},{"Code": "BSA20","Name": "Thuế GTGT được khấu trừ"},{"Code": "BSA21","Name": "Thuế và các khoản khác phải thu Nhà nước"},{"Code": "BSA160","Name": "Giao dịch mua bán lại trái phiếu chính phủ"},{"Code": "BSA22","Name": "Tài sản ngắn hạn khác"},{"Code": "BSA23","Name": "Tài sản dài hạn"},{"Code": "BSA24","Name": "Các khoản phải thu dài hạn"},{"Code": "BSA25","Name": "Phải thu dài hạn của khách hàng"},{"Code": "BSA161","Name": "Trả trước dài hạn người bán"},{"Code": "BSS134","Name": "Vốn kinh doanh ở đơn vị trực thuộc"},{"Code": "BSA26","Name": "Phải thu dài hạn nội bộ"},{"Code": "BSA162","Name": "Phải thu về cho vay dài hạn"},{"Code": "BSA27","Name": "Phải thu dài hạn khác"},{"Code": "BSA28","Name": "Dự phòng phải thu dài hạn khó đòi"},{"Code": "BSA29","Name": "Tài sản cố định"},{"Code": "BSA30","Name": "Tài sản cố định hữu hình"},{"Code": "BSA33","Name": "Tài sản cố định thuê tài chính"},{"Code": "BSA36","Name": "Tài sản cố định vô hình"},{"Code": "BSA40","Name": "Bất động sản đầu tư"},{"Code": "BSA41","Name": "Nguyên giá bất động sản đầu tư"},{"Code": "BSA42","Name": "Hao mòn bất động sản đầu tư"},{"Code": "BSA163","Name": "Tài sản dở dang dài hạn"},{"Code": "BSA164","Name": "Chi phí sản xuất, kinh doanh dở dang dài hạn"},{"Code": "BSA188","Name": "Chi phí xây dựng cơ bản dở dang "},{"Code": "BSA43","Name": "Các khoản đầu tư tài chính dài hạn"},{"Code": "BSA44","Name": "Đầu tư vào công ty con"},{"Code": "BSA45","Name": "Đầu tư vào công ty liên kết, liên doanh"},{"Code": "BSA46","Name": "Đầu tư dài hạn khác"},{"Code": "BSA47","Name": "Dự phòng giảm giá đầu tư tài chính dài hạn"},{"Code": "BSA165","Name": "Đầu tư dài hạn giữ đến ngày đáo hạn"},{"Code": "BSA49","Name": "Tài sản dài hạn khác"},{"Code": "BSA50","Name": "Chi phí trả trước dài hạn"},{"Code": "BSA51","Name": "Tài sản thuế thu nhập hoãn lại"},{"Code": "BSA166","Name": "Thiết bị, vật tư, phụ tùng thay thế dài hạn"},{"Code": "BSA52","Name": "Tài sản dài hạn khác"},{"Code": "BSA209","Name": "Lợi thế thương mại"},{"Code": "BSA53","Name": "TỔNG CỘNG TÀI SẢN"},{"Code": "BSA54","Name": "Nợ phải trả"},{"Code": "BSA55","Name": "Nợ ngắn hạn"},{"Code": "BSA56","Name": "Vay và nợ ngắn hạn"},{"Code": "BSA57","Name": "Phải trả người bán"},{"Code": "BSA58","Name": "Người mua trả tiền trước"},{"Code": "BSA59","Name": "Thuế và các khoản phải nộp Nhà nước"},{"Code": "BSA60","Name": "Phải trả người lao động"},{"Code": "BSA61","Name": "Chi phí phải trả"},{"Code": "BSA62","Name": "Phải trả nội bộ"},{"Code": "BSA63","Name": "Phải trả theo tiến độ kế hoạch hợp đồng xây dựng"},{"Code": "BSA64","Name": "Các khoản phải trả, phải nộp ngắn hạn khác"},{"Code": "BSA66","Name": "Quỹ khen thưởng, phúc lợi"},{"Code": "BSA167","Name": "Doanh thu chưa thực hiện ngắn hạn"},{"Code": "BSA65","Name": "Dự phòng phải trả ngắn hạn"},{"Code": "BSA168","Name": "Quỹ bình ổn giá"},{"Code": "BSA169","Name": "Giao dịch mua bán lại trái phiếu chính phủ"},{"Code": "BSA67","Name": "Nợ dài hạn"},{"Code": "BSA68","Name": "Phải trả dài hạn người bán"},{"Code": "BSA170","Name": "Người mua trả trước dài hạn"},{"Code": "BSA171","Name": "Chi phí phải trả dài hạn"},{"Code": "BSA172","Name": "Phải trả nội bộ về vốn kinh doanh"},{"Code": "BSA69","Name": "Phải trả dài hạn nội bộ"},{"Code": "BSA70","Name": "Phải trả dài hạn khác"},{"Code": "BSA71","Name": "Vay và nợ dài hạn"},{"Code": "BSA173","Name": "Trái phiếu chuyển đổi"},{"Code": "BSA174","Name": "Cổ phiếu ưu đãi"},{"Code": "BSA72","Name": "Thuế thu nhập hoãn lại phải trả"},{"Code": "BSA73","Name": "Dự phòng trợ cấp mất việc làm"},{"Code": "BSA76","Name": "Doanh thu chưa thực hiện dài hạn"},{"Code": "BSA77","Name": "Quỹ phát triển khoa học và công nghệ"},{"Code": "BSA74","Name": "Dự phòng phải trả dài hạn"},{"Code": "BSA78","Name": "Vốn chủ sở hữu"},{"Code": "BSA79","Name": "Vốn và các quỹ"},{"Code": "BSA80","Name": "Vốn góp"},{"Code": "BSA81","Name": "Thặng dư vốn cổ phần"},{"Code": "BSA176","Name": "Quyền chọn chuyển đổi trái phiếu"},{"Code": "BSA82","Name": "Vốn khác của chủ sở hữu"},{"Code": "BSA83","Name": "Cổ phiếu quỹ"},{"Code": "BSA84","Name": "Chênh lệch đánh giá lại tài sản"},{"Code": "BSA85","Name": "Chênh lệch tỷ giá hối đoái"},{"Code": "BSA86","Name": "Quỹ đầu tư phát triển"},{"Code": "BSA87","Name": "Quỹ dự phòng tài chính"},{"Code": "BSA89","Name": "Quỹ khác thuộc vốn chủ sở hữu"},{"Code": "BSA90","Name": "Lợi nhuận sau thuế chưa phân phối"},{"Code": "BSA210","Name": "Lợi ích cổ đông không kiểm soát"},{"Code": "BSA91","Name": "Quỹ hỗ trợ sắp xếp doanh nghiệp"},{"Code": "BSA93","Name": "Nguồn vốn đầu tư XDCB"},{"Code": "BSA92","Name": "Nguồn kinh phí và quỹ khác"},{"Code": "BSA94","Name": "Vốn ngân sách nhà nước"},{"Code": "BSA211","Name": "Nguồn kinh phí đã hình thành TSCĐ"},{"Code": "BSA96","Name": "TỔNG CỘNG NGUỒN VỐN"}]
    df_api.columns = df_api.columns.str.upper()

    for i in range(len(mapping)):
        df_api.rename(columns={mapping[i]["Code"]: mapping[i]["Name"]},inplace=True)
    return df_api[0].to_json()

def getInfoCB(code):
    api_url = f"https://fwtapi3.fialda.com/api/services/app/Market/GetICBInfos?icbCode={code}"
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
    return df_api.to_json()

def getInfoCBName():
    icb_data = pd.read_excel("../stock_data/icb_info.xlsx")
    return icb_data.to_json()

@app.route("/info_4m", methods=["POST"])
def cal4M():
    data = request.get_json()
    print(data)
    symbol = data.get("symbol")
    if symbol is None:
        abort(400)
    return jsonify({"4m": calculate4M(symbol)})

@app.route("/info_canslim", methods=["POST"])
def calCanslim():
    data = request.get_json()
    print(data)
    symbol = data.get("symbol")
    if symbol is None:
        abort(400)
    return jsonify({"4m": canslim(symbol)})

@app.route("/info_stockname", methods=["POST"])
def stockName():
    data = request.get_json()
    print(data)
    symbol = data.get("symbol")
    if symbol is None:
        abort(400)
    return jsonify({"StockName": getStockName(symbol)})

@app.route("/info_icb", methods=["GET"])
def getInfoICB():
    result = getInfoCBName()
    try:
        json_result = jsonify(result)
        return json_result
    except (TypeError, ValueError):
        abort(500)

@app.route("/info_stockprice", methods=["POST"])
def stockPrice():
    data = request.get_json()
    print(data)
    symbol = data.get("symbol")
    if symbol is None:
        abort(400)

    result = getStockPrice(symbol)
    try:
        json_result = jsonify(result)
        return json_result
    except (TypeError, ValueError):
        abort(500)

@app.route("/info_kqkd", methods=["POST"])
def KQKD():
    data = request.get_json()
    print(data)
    symbol = data.get("symbol")
    isQuarterReport = data.get("isQuarterReport")
    if symbol is None:
        abort(400)

    result = getKQKD(symbol, isQuarterReport)
    try:
        json_result = jsonify(result)
        return json_result
    except (TypeError, ValueError):
        abort(500)

@app.route("/info_cdkt", methods=["POST"])
def CDKT():
    data = request.get_json()
    print(data)
    symbol = data.get("symbol")
    isQuarterReport = data.get("isQuarterReport")
    if symbol is None:
        abort(400)

    result = getCDKT(symbol, isQuarterReport)
    try:
        json_result = jsonify(result)
        return json_result
    except (TypeError, ValueError):
        abort(500)

@app.route("/info_nganh", methods=["POST"])
def info_nganh():
    data = request.get_json()
    print(data)
    name = data.get("name")
    if name is None:
        abort(400)

    icb_df = pd.read_excel('../stock_data/icb_info.xlsx')
    code = icb_df[icb_df["icbName"] == name].icbCode.values[0]

    result = getInfoCB(code)
    try:
        json_result = jsonify(result)
        return json_result
    except (TypeError, ValueError):
        abort(500)



if __name__ == "__main__":
    app.run(debug=True)
