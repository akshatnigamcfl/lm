from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from datetime import date, datetime, timezone, timedelta
from django.db.models import OuterRef, Subquery
from leads.models import *
from dropdown.models import *


from account.views import *
from account.serializers import *


# Create your views here.


def loginFun(request):
    if request.POST:
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(email=email, password=password)
        if user != None and user.visibility == True:
            login(request,user)
            token = get_tokens_for_user(user)
            print('token',token)
            
            response =  HttpResponseRedirect(reverse(dashboardFun))
            response.set_cookie('access', token['access'], max_age=360000)
            response.set_cookie('refresh', token['refresh'], max_age=360000)
            return response
        else:
            messages.error(request, 'invalid credentials!')

    return HttpResponse(render(request, 'login.html', context={'data':"no data"}))




@login_required(login_url='/login')
def logoutFun(request):
    logout(request)
    return redirect('/login')


@login_required(login_url='/login')
def my_infoFun(request):

    employee_leave_instance = EmployeeLeaves.objects.filter(status__title='pending', employee__reporting_manager__id=request.user.id).values()

    return HttpResponse(render(request, 'my_info.html', context={'data':"no data"}))



@login_required(login_url='/login')
def hardReset(request):
    # Bramha-Astra

    Leads.objects.all().delete()
    ServiceCategory.objects.all().delete()
    LeadHistory.objects.all().delete()
    
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("UPDATE sqlite_sequence SET seq=0 WHERE name='leads_leads'")
        cursor.execute("UPDATE sqlite_sequence SET seq=0 WHERE name='leads_status_history'")
        cursor.execute("UPDATE sqlite_sequence SET seq=0 WHERE name='leads_service_category_status_history'")
        cursor.execute("UPDATE sqlite_sequence SET seq=0 WHERE name='leads_remark'")
        cursor.execute("UPDATE sqlite_sequence SET seq=0 WHERE name='leads_remark_history'")
        cursor.execute("UPDATE sqlite_sequence SET seq=0 WHERE name='leads_leads_service_category'")
        cursor.execute("UPDATE sqlite_sequence SET seq=0 WHERE name='leads_service_category'")
        cursor.execute("UPDATE sqlite_sequence SET seq=0 WHERE name='leads_service_category_lead_history'")
        cursor.execute("UPDATE sqlite_sequence SET seq=0 WHERE name='leads_service_category_follow_up'")
        cursor.execute("UPDATE sqlite_sequence SET seq=0 WHERE name='leads_marketplace'")
        cursor.execute("UPDATE sqlite_sequence SET seq=0 WHERE name='leads_program'")
        cursor.execute("UPDATE sqlite_sequence SET seq=0 WHERE name='leads_leadhistory'")

    # dashboardFun(request)
    return HttpResponseRedirect(reverse(dashboardFun))



@login_required
def customUpload(reqeust):

    a = [{"id":1,"name":"Afghanistan","dial_code":"+93","code":"AF"},{"id":2,"name":"Aland Islands","dial_code":"+358","code":"AX"},{"id":3,"name":"Albania","dial_code":"+355","code":"AL"},{"id":4,"name":"Algeria","dial_code":"+213","code":"DZ"},{"id":5,"name":"AmericanSamoa","dial_code":"+1684","code":"AS"},{"id":6,"name":"Andorra","dial_code":"+376","code":"AD"},{"id":7,"name":"Angola","dial_code":"+244","code":"AO"},{"id":8,"name":"Anguilla","dial_code":"+1264","code":"AI"},{"id":9,"name":"Antarctica","dial_code":"+672","code":"AQ"},{"id":10,"name":"Antigua and Barbuda","dial_code":"+1268","code":"AG"},{"id":11,"name":"Argentina","dial_code":"+54","code":"AR"},{"id":12,"name":"Armenia","dial_code":"+374","code":"AM"},{"id":13,"name":"Aruba","dial_code":"+297","code":"AW"},{"id":14,"name":"Australia","dial_code":"+61","code":"AU"},{"id":15,"name":"Austria","dial_code":"+43","code":"AT"},{"id":16,"name":"Azerbaijan","dial_code":"+994","code":"AZ"},{"id":17,"name":"Bahamas","dial_code":"+1242","code":"BS"},{"id":18,"name":"Bahrain","dial_code":"+973","code":"BH"},{"id":19,"name":"Bangladesh","dial_code":"+880","code":"BD"},{"id":20,"name":"Barbados","dial_code":"+1246","code":"BB"},{"id":21,"name":"Belarus","dial_code":"+375","code":"BY"},{"id":22,"name":"Belgium","dial_code":"+32","code":"BE"},{"id":23,"name":"Belize","dial_code":"+501","code":"BZ"},{"id":24,"name":"Benin","dial_code":"+229","code":"BJ"},{"id":25,"name":"Bermuda","dial_code":"+1441","code":"BM"},{"id":26,"name":"Bhutan","dial_code":"+975","code":"BT"},{"id":27,"name":"Bolivia, Plurinational State of","dial_code":"+591","code":"BO"},{"id":28,"name":"Bosnia and Herzegovina","dial_code":"+387","code":"BA"},{"id":29,"name":"Botswana","dial_code":"+267","code":"BW"},{"id":30,"name":"Brazil","dial_code":"+55","code":"BR"},{"id":31,"name":"British Indian Ocean Territory","dial_code":"+246","code":"IO"},{"id":32,"name":"Brunei Darussalam","dial_code":"+673","code":"BN"},{"id":33,"name":"Bulgaria","dial_code":"+359","code":"BG"},{"id":34,"name":"Burkina Faso","dial_code":"+226","code":"BF"},{"id":35,"name":"Burundi","dial_code":"+257","code":"BI"},{"id":36,"name":"Cambodia","dial_code":"+855","code":"KH"},{"id":37,"name":"Cameroon","dial_code":"+237","code":"CM"},{"id":38,"name":"Canada","dial_code":"+1","code":"CA"},{"id":39,"name":"Cape Verde","dial_code":"+238","code":"CV"},{"id":40,"name":"Cayman Islands","dial_code":"+ 345","code":"KY"},{"id":41,"name":"Central African Republic","dial_code":"+236","code":"CF"},{"id":42,"name":"Chad","dial_code":"+235","code":"TD"},{"id":43,"name":"Chile","dial_code":"+56","code":"CL"},{"id":44,"name":"China","dial_code":"+86","code":"CN"},{"id":45,"name":"Christmas Island","dial_code":"+61","code":"CX"},{"id":46,"name":"Cocos (Keeling) Islands","dial_code":"+61","code":"CC"},{"id":47,"name":"Colombia","dial_code":"+57","code":"CO"},{"id":48,"name":"Comoros","dial_code":"+269","code":"KM"},{"id":49,"name":"Congo","dial_code":"+242","code":"CG"},{"id":50,"name":"Congo, The Democratic Republic of the Congo","dial_code":"+243","code":"CD"},{"id":51,"name":"Cook Islands","dial_code":"+682","code":"CK"},{"id":52,"name":"Costa Rica","dial_code":"+506","code":"CR"},{"id":53,"name":"Cote d'Ivoire","dial_code":"+225","code":"CI"},{"id":54,"name":"Croatia","dial_code":"+385","code":"HR"},{"id":55,"name":"Cuba","dial_code":"+53","code":"CU"},{"id":56,"name":"Cyprus","dial_code":"+357","code":"CY"},{"id":57,"name":"Czech Republic","dial_code":"+420","code":"CZ"},{"id":58,"name":"Denmark","dial_code":"+45","code":"DK"},{"id":59,"name":"Djibouti","dial_code":"+253","code":"DJ"},{"id":60,"name":"Dominica","dial_code":"+1767","code":"DM"},{"id":61,"name":"Dominican Republic","dial_code":"+1849","code":"DO"},{"id":62,"name":"Ecuador","dial_code":"+593","code":"EC"},{"id":63,"name":"Egypt","dial_code":"+20","code":"EG"},{"id":64,"name":"El Salvador","dial_code":"+503","code":"SV"},{"id":65,"name":"Equatorial Guinea","dial_code":"+240","code":"GQ"},{"id":66,"name":"Eritrea","dial_code":"+291","code":"ER"},{"id":67,"name":"Estonia","dial_code":"+372","code":"EE"},{"id":68,"name":"Ethiopia","dial_code":"+251","code":"ET"},{"id":69,"name":"Falkland Islands (Malvinas)","dial_code":"+500","code":"FK"},{"id":70,"name":"Faroe Islands","dial_code":"+298","code":"FO"},{"id":71,"name":"Fiji","dial_code":"+679","code":"FJ"},{"id":72,"name":"Finland","dial_code":"+358","code":"FI"},{"id":73,"name":"France","dial_code":"+33","code":"FR"},{"id":74,"name":"French Guiana","dial_code":"+594","code":"GF"},{"id":75,"name":"French Polynesia","dial_code":"+689","code":"PF"},{"id":76,"name":"Gabon","dial_code":"+241","code":"GA"},{"id":77,"name":"Gambia","dial_code":"+220","code":"GM"},{"id":78,"name":"Georgia","dial_code":"+995","code":"GE"},{"id":79,"name":"Germany","dial_code":"+49","code":"DE"},{"id":80,"name":"Ghana","dial_code":"+233","code":"GH"},{"id":81,"name":"Gibraltar","dial_code":"+350","code":"GI"},{"id":82,"name":"Greece","dial_code":"+30","code":"GR"},{"id":83,"name":"Greenland","dial_code":"+299","code":"GL"},{"id":84,"name":"Grenada","dial_code":"+1473","code":"GD"},{"id":85,"name":"Guadeloupe","dial_code":"+590","code":"GP"},{"id":86,"name":"Guam","dial_code":"+1671","code":"GU"},{"id":87,"name":"Guatemala","dial_code":"+502","code":"GT"},{"id":88,"name":"Guernsey","dial_code":"+44","code":"GG"},{"id":89,"name":"Guinea","dial_code":"+224","code":"GN"},{"id":90,"name":"Guinea-Bissau","dial_code":"+245","code":"GW"},{"id":91,"name":"Guyana","dial_code":"+595","code":"GY"},{"id":92,"name":"Haiti","dial_code":"+509","code":"HT"},{"id":93,"name":"Holy See (Vatican City State)","dial_code":"+379","code":"VA"},{"id":94,"name":"Honduras","dial_code":"+504","code":"HN"},{"id":95,"name":"Hong Kong","dial_code":"+852","code":"HK"},{"id":96,"name":"Hungary","dial_code":"+36","code":"HU"},{"id":97,"name":"Iceland","dial_code":"+354","code":"IS"},{"id":98,"name":"India","dial_code":"+91","code":"IN"},{"id":99,"name":"Indonesia","dial_code":"+62","code":"ID"},{"id":100,"name":"Iran, Islamic Republic of Persian Gulf","dial_code":"+98","code":"IR"},{"id":101,"name":"Iraq","dial_code":"+964","code":"IQ"},{"id":102,"name":"Ireland","dial_code":"+353","code":"IE"},{"id":103,"name":"Isle of Man","dial_code":"+44","code":"IM"},{"id":104,"name":"Israel","dial_code":"+972","code":"IL"},{"id":105,"name":"Italy","dial_code":"+39","code":"IT"},{"id":106,"name":"Jamaica","dial_code":"+1876","code":"JM"},{"id":107,"name":"Japan","dial_code":"+81","code":"JP"},{"id":108,"name":"Jersey","dial_code":"+44","code":"JE"},{"id":109,"name":"Jordan","dial_code":"+962","code":"JO"},{"id":110,"name":"Kazakhstan","dial_code":"+77","code":"KZ"},{"id":111,"name":"Kenya","dial_code":"+254","code":"KE"},{"id":112,"name":"Kiribati","dial_code":"+686","code":"KI"},{"id":113,"name":"Korea, Democratic People's Republic of Korea","dial_code":"+850","code":"KP"},{"id":114,"name":"Korea, Republic of South Korea","dial_code":"+82","code":"KR"},{"id":115,"name":"Kuwait","dial_code":"+965","code":"KW"},{"id":116,"name":"Kyrgyzstan","dial_code":"+996","code":"KG"},{"id":117,"name":"Laos","dial_code":"+856","code":"LA"},{"id":118,"name":"Latvia","dial_code":"+371","code":"LV"},{"id":119,"name":"Lebanon","dial_code":"+961","code":"LB"},{"id":120,"name":"Lesotho","dial_code":"+266","code":"LS"},{"id":121,"name":"Liberia","dial_code":"+231","code":"LR"},{"id":122,"name":"Libyan Arab Jamahiriya","dial_code":"+218","code":"LY"},{"id":123,"name":"Liechtenstein","dial_code":"+423","code":"LI"},{"id":124,"name":"Lithuania","dial_code":"+370","code":"LT"},{"id":125,"name":"Luxembourg","dial_code":"+352","code":"LU"},{"id":126,"name":"Macao","dial_code":"+853","code":"MO"},{"id":127,"name":"Macedonia","dial_code":"+389","code":"MK"},{"id":128,"name":"Madagascar","dial_code":"+261","code":"MG"},{"id":129,"name":"Malawi","dial_code":"+265","code":"MW"},{"id":130,"name":"Malaysia","dial_code":"+60","code":"MY"},{"id":131,"name":"Maldives","dial_code":"+960","code":"MV"},{"id":132,"name":"Mali","dial_code":"+223","code":"ML"},{"id":133,"name":"Malta","dial_code":"+356","code":"MT"},{"id":134,"name":"Marshall Islands","dial_code":"+692","code":"MH"},{"id":135,"name":"Martinique","dial_code":"+596","code":"MQ"},{"id":136,"name":"Mauritania","dial_code":"+222","code":"MR"},{"id":137,"name":"Mauritius","dial_code":"+230","code":"MU"},{"id":138,"name":"Mayotte","dial_code":"+262","code":"YT"},{"id":139,"name":"Mexico","dial_code":"+52","code":"MX"},{"id":140,"name":"Micronesia, Federated States of Micronesia","dial_code":"+691","code":"FM"},{"id":141,"name":"Moldova","dial_code":"+373","code":"MD"},{"id":142,"name":"Monaco","dial_code":"+377","code":"MC"},{"id":143,"name":"Mongolia","dial_code":"+976","code":"MN"},{"id":144,"name":"Montenegro","dial_code":"+382","code":"ME"},{"id":145,"name":"Montserrat","dial_code":"+1664","code":"MS"},{"id":146,"name":"Morocco","dial_code":"+212","code":"MA"},{"id":147,"name":"Mozambique","dial_code":"+258","code":"MZ"},{"id":148,"name":"Myanmar","dial_code":"+95","code":"MM"},{"id":149,"name":"Namibia","dial_code":"+264","code":"NA"},{"id":150,"name":"Nauru","dial_code":"+674","code":"NR"},{"id":151,"name":"Nepal","dial_code":"+977","code":"NP"},{"id":152,"name":"Netherlands","dial_code":"+31","code":"NL"},{"id":153,"name":"Netherlands Antilles","dial_code":"+599","code":"AN"},{"id":154,"name":"New Caledonia","dial_code":"+687","code":"NC"},{"id":155,"name":"New Zealand","dial_code":"+64","code":"NZ"},{"id":156,"name":"Nicaragua","dial_code":"+505","code":"NI"},{"id":157,"name":"Niger","dial_code":"+227","code":"NE"},{"id":158,"name":"Nigeria","dial_code":"+234","code":"NG"},{"id":159,"name":"Niue","dial_code":"+683","code":"NU"},{"id":160,"name":"Norfolk Island","dial_code":"+672","code":"NF"},{"id":161,"name":"Northern Mariana Islands","dial_code":"+1670","code":"MP"},{"id":162,"name":"Norway","dial_code":"+47","code":"NO"},{"id":163,"name":"Oman","dial_code":"+968","code":"OM"},{"id":164,"name":"Pakistan","dial_code":"+92","code":"PK"},{"id":165,"name":"Palau","dial_code":"+680","code":"PW"},{"id":166,"name":"Palestinian Territory, Occupied","dial_code":"+970","code":"PS"},{"id":167,"name":"Panama","dial_code":"+507","code":"PA"},{"id":168,"name":"Papua New Guinea","dial_code":"+675","code":"PG"},{"id":169,"name":"Paraguay","dial_code":"+595","code":"PY"},{"id":170,"name":"Peru","dial_code":"+51","code":"PE"},{"id":171,"name":"Philippines","dial_code":"+63","code":"PH"},{"id":172,"name":"Pitcairn","dial_code":"+872","code":"PN"},{"id":173,"name":"Poland","dial_code":"+48","code":"PL"},{"id":174,"name":"Portugal","dial_code":"+351","code":"PT"},{"id":175,"name":"Puerto Rico","dial_code":"+1939","code":"PR"},{"id":176,"name":"Qatar","dial_code":"+974","code":"QA"},{"id":177,"name":"Romania","dial_code":"+40","code":"RO"},{"id":178,"name":"Russia","dial_code":"+7","code":"RU"},{"id":179,"name":"Rwanda","dial_code":"+250","code":"RW"},{"id":180,"name":"Reunion","dial_code":"+262","code":"RE"},{"id":181,"name":"Saint Barthelemy","dial_code":"+590","code":"BL"},{"id":182,"name":"Saint Helena, Ascension and Tristan Da Cunha","dial_code":"+290","code":"SH"},{"id":183,"name":"Saint Kitts and Nevis","dial_code":"+1869","code":"KN"},{"id":184,"name":"Saint Lucia","dial_code":"+1758","code":"LC"},{"id":185,"name":"Saint Martin","dial_code":"+590","code":"MF"},{"id":186,"name":"Saint Pierre and Miquelon","dial_code":"+508","code":"PM"},{"id":187,"name":"Saint Vincent and the Grenadines","dial_code":"+1784","code":"VC"},{"id":188,"name":"Samoa","dial_code":"+685","code":"WS"},{"id":189,"name":"San Marino","dial_code":"+378","code":"SM"},{"id":190,"name":"Sao Tome and Principe","dial_code":"+239","code":"ST"},{"id":191,"name":"Saudi Arabia","dial_code":"+966","code":"SA"},{"id":192,"name":"Senegal","dial_code":"+221","code":"SN"},{"id":193,"name":"Serbia","dial_code":"+381","code":"RS"},{"id":194,"name":"Seychelles","dial_code":"+248","code":"SC"},{"id":195,"name":"Sierra Leone","dial_code":"+232","code":"SL"},{"id":196,"name":"Singapore","dial_code":"+65","code":"SG"},{"id":197,"name":"Slovakia","dial_code":"+421","code":"SK"},{"id":198,"name":"Slovenia","dial_code":"+386","code":"SI"},{"id":199,"name":"Solomon Islands","dial_code":"+677","code":"SB"},{"id":200,"name":"Somalia","dial_code":"+252","code":"SO"},{"id":201,"name":"South Africa","dial_code":"+27","code":"ZA"},{"id":202,"name":"South Sudan","dial_code":"+211","code":"SS"},{"id":203,"name":"South Georgia and the South Sandwich Islands","dial_code":"+500","code":"GS"},{"id":204,"name":"Spain","dial_code":"+34","code":"ES"},{"id":205,"name":"Sri Lanka","dial_code":"+94","code":"LK"},{"id":206,"name":"Sudan","dial_code":"+249","code":"SD"},{"id":207,"name":"Suriname","dial_code":"+597","code":"SR"},{"id":208,"name":"Svalbard and Jan Mayen","dial_code":"+47","code":"SJ"},{"id":209,"name":"Swaziland","dial_code":"+268","code":"SZ"},{"id":210,"name":"Sweden","dial_code":"+46","code":"SE"},{"id":211,"name":"Switzerland","dial_code":"+41","code":"CH"},{"id":212,"name":"Syrian Arab Republic","dial_code":"+963","code":"SY"},{"id":213,"name":"Taiwan","dial_code":"+886","code":"TW"},{"id":214,"name":"Tajikistan","dial_code":"+992","code":"TJ"},{"id":215,"name":"Tanzania, United Republic of Tanzania","dial_code":"+255","code":"TZ"},{"id":216,"name":"Thailand","dial_code":"+66","code":"TH"},{"id":217,"name":"Timor-Leste","dial_code":"+670","code":"TL"},{"id":218,"name":"Togo","dial_code":"+228","code":"TG"},{"id":219,"name":"Tokelau","dial_code":"+690","code":"TK"},{"id":220,"name":"Tonga","dial_code":"+676","code":"TO"},{"id":221,"name":"Trinidad and Tobago","dial_code":"+1868","code":"TT"},{"id":222,"name":"Tunisia","dial_code":"+216","code":"TN"},{"id":223,"name":"Turkey","dial_code":"+90","code":"TR"},{"id":224,"name":"Turkmenistan","dial_code":"+993","code":"TM"},{"id":225,"name":"Turks and Caicos Islands","dial_code":"+1649","code":"TC"},{"id":226,"name":"Tuvalu","dial_code":"+688","code":"TV"},{"id":227,"name":"Uganda","dial_code":"+256","code":"UG"},{"id":228,"name":"Ukraine","dial_code":"+380","code":"UA"},{"id":229,"name":"United Arab Emirates","dial_code":"+971","code":"AE"},{"id":230,"name":"United Kingdom","dial_code":"+44","code":"GB"},{"id":231,"name":"United States","dial_code":"+1","code":"US"},{"id":232,"name":"Uruguay","dial_code":"+598","code":"UY"},{"id":233,"name":"Uzbekistan","dial_code":"+998","code":"UZ"},{"id":234,"name":"Vanuatu","dial_code":"+678","code":"VU"},{"id":235,"name":"Venezuela, Bolivarian Republic of Venezuela","dial_code":"+58","code":"VE"},{"id":236,"name":"Vietnam","dial_code":"+84","code":"VN"},{"id":237,"name":"Virgin Islands, British","dial_code":"+1284","code":"VG"},{"id":238,"name":"Virgin Islands, U.S.","dial_code":"+1340","code":"VI"},{"id":239,"name":"Wallis and Futuna","dial_code":"+681","code":"WF"},{"id":240,"name":"Yemen","dial_code":"+967","code":"YE"},{"id":241,"name":"Zambia","dial_code":"+260","code":"ZM"},{"id":242,"name":"Zimbabwe","dial_code":"+263","code":"ZW"}]


    for b in a:
        CountryCode.objects.create( name= b['name'], dial_code=b['dial_code'], code=b['code'])


    return HttpResponseRedirect(reverse(dashboardFun))
    


@login_required(login_url='/login')
def dashboardFun(request):

    def getParams(request):
        try:
            date_type = request.GET.get('date_type')
            if not date_type:
                date_type = 'this_month'
        except:
                date_type = 'this_month'

        try:
            data_type = request.GET.get('data_type')
            if not data_type:
                data_type = 'overall_performance'
        except:
                data_type = 'overall_performance'

        return {'date_type': date_type, 'data_type': data_type}

    paramsdata = getParams(request)
    date_type = paramsdata['date_type']
    data_type = paramsdata['data_type']

    if date_type == 'this_month':
        main_date = datetime.now().month
        # print('main_date',main_date)
    if date_type == 'last_week':
        today = datetime.now().date()
        start_date = today - timedelta(days=today.weekday() + 7)
        last_date = today - timedelta(days=today.weekday() + 1)
    if date_type == 'last_month':
        main_date = datetime.now().month-1
    if date_type == 'last_7_days':
        start_date = datetime.now().date() - timedelta(days=6)
        last_date = datetime.now().date()
    if date_type == 'last_30_days':
        start_date = datetime.now().date() - timedelta(days=29)
        last_date = datetime.now().date()
    if date_type == 'last_60_days':
        start_date = datetime.now().date() - timedelta(days=59)
        last_date = datetime.now().date()
    if date_type == 'custom':
        start_date = datetime.strptime(request.GET.get('date_from'), "%Y-%m-%d").date()
        last_date = datetime.strptime(request.GET.get('date_to'), "%Y-%m-%d").date()
        # print(start_date, last_date)


    primary_data = []
    secondary_data = []


    if request.user.user_role.filter(title='super_admin').exists() or request.user.is_admin == True:
        if date_type == 'this_month' or date_type == 'last_month':
            leadsData = ServiceCategory.objects.filter(created_date__month=main_date)
            # pitch_in_progress = Service_category.objects.filter( Q(status_history__status_date__month=main_date), Q(status_history__status__title='pitch in progress') )
            all_leads = ServiceCategory.objects.all()
            for al in all_leads:
                if al.status_history.filter( Q(status_date__month=main_date)).order_by('-id').first():
                    primary_data.append({'lead_id': al, 'status': al.status_history.filter( Q(status_date__month=main_date)).order_by('-id').first().status.title })

        else:
            leadsData = ServiceCategory.objects.filter(created_date__range=[start_date, last_date])
            all_leads = ServiceCategory.objects.all()
            for al in all_leads:
                if al.status_history.filter( Q(status_date__range=[start_date, last_date])).order_by('-id').first() != None:
                    primary_data.append({'lead_id': al, 'status': al.status_history.filter( Q(status_date__range=[start_date, last_date])).order_by('-id').first().status.title })
            # open_leads_instance = Service_category.objects.filter(Q(status_history__status_date__range = [start_date, last_date]))


        def associate_performance():
            def associate_performance_fun(data, lead_id):
                if lead_id.status_history.all().order_by('-id').first().status.title == 'subscription_started':
                    data['subscription_started'].append(lead_id)
                elif lead_id.status_history.all().order_by('-id').first().status.title == 'follow_up_unresponsive':
                    data['follow_up_unresponsive'].append(lead_id)
                elif lead_id.status_history.all().order_by('-id').first().status.title == 'not_interested':
                    data['not_interested'].append(lead_id)
                else:
                    data['open'].append(lead_id)

                data['assigned'].append(lead_id)
                data['name'] = (lead_id.associate)

            def associate_performance_append_fun(secondary_data):
                # if len(secondary_data) != 0:
                for o in secondary_data:
                    if o['name'] == m['lead_id'].associate:
                        associate_performance_fun(o, m['lead_id'])
                        break
                else:
                    # if o['name'] != m['lead_id'].associate: 
                        print('working once')
                        associate_performance_fun(scr_data, m['lead_id'])
                        secondary_data.append(scr_data)
                # else:
                #     associate_performance_fun(scr_data, m['lead_id'])
                #     secondary_data.append(scr_data)

            for m in primary_data:
                scr_data = { 'name': '',  "assigned": [], 'open': [], 'subscription_started': [], 'follow_up_unresponsive': [], 'not_interested': [] }
                if date_type == 'this_month' or date_type == 'last_month':
                    if m['lead_id'].created_date.month == main_date:
                        if m['lead_id'].associate !=None :
                            associate_performance_append_fun(secondary_data)
                else:
                    if start_date <= m['lead_id'].created_date.date() <= last_date:
                        if m['lead_id'].associate !=None :
                            associate_performance_append_fun(secondary_data)

        if data_type == 'overall_performance':
            associate_performance()
            main_data = secondary_data
            secondary_data = []

            def dataShift(sd, scr):
                for asng in sd['assigned']:
                    scr['assigned'].append(asng)
                for asng in sd['open']:
                    scr['open'].append(asng)
                for asng in sd['subscription_started']:
                    scr['subscription_started'].append(asng)
                for asng in sd['follow_up_unresponsive']:
                    scr['follow_up_unresponsive'].append(asng)
                for asng in sd['not_interested']:
                    scr['not_interested'].append(asng)

            for sd in main_data:
                scr_data = {'name': '', 'unassigned_leads': [],'assigned': [], 'open': [], 'subscription_started': [], 'follow_up_unresponsive': [], 'not_interested': []}
                # if len(secondary_data) != 0:
                for scr in secondary_data:
                    if scr['name'] == sd['name'].reporting_manager:
                        dataShift(sd, scr)
                        # secondary_data.append(scr)
                        break

                else:
                    # if scr['name'] != sd['name'].team_leader:
                    scr_data['name'] = sd['name'].reporting_manager
                    for m in primary_data:
                        if m['lead_id'].assigned_manager == sd['name'].reporting_manager and m['lead_id'].associate == None:
                            scr_data['unassigned_leads'].append(m)
                    dataShift(sd, scr_data)
                    secondary_data.append(scr_data)
                    # break
                # else:
                #     scr_data['name'] = sd['name'].team_leader
                #     dataShift(sd, scr_data)
                #     secondary_data.append(scr_data)

        elif data_type == 'associate_level_performance':
            associate_performance()

        elif data_type == 'service_level_performance':
            def dataShift(sd, scr):
                scr['assigned'].append(sd)
                lead_status = sd.status_history.filter( Q(status_date__month=main_date)).order_by('-id').first().status.title
                if lead_status == 'subscription_started':
                    scr['subscription_started'].append(sd)
                elif lead_status == 'follow_up_unresponsive':
                    scr['follow_up_unresponsive'].append(sd)
                elif lead_status == 'not_interested':
                    scr['not_interested'].append(sd)
                else:
                    scr['open_leads'].append(sd)

            for sd in leadsData:
                scr_data = {'marketplace': '', 'service': '', 'assigned': [], 'open_leads': [], 'subscription_started': [], 'follow_up_unresponsive': [], 'not_interested': []}
                for scr in secondary_data:
                    print('working 1', scr)
                    if scr['marketplace'] == sd.service.marketplace and scr['service'] == sd.service.service:
                        dataShift(sd, scr)
                        break
                else:
                    scr_data['marketplace'] = sd.service.marketplace
                    scr_data['service'] = sd.service.service
                    dataShift(sd, scr_data)
                    secondary_data.append(scr_data)


    # elif request.user.user_role.filter(title='super_admin').exists():

    elif request.user.user_role.filter(title='business_development_team_lead').exists():
        # if date_type == 'this_month' or date_type == 'last_month':
            # fresh_assigned_intance = Service_category.objects.filter(created_date__month=main_date)
            # open_leads_intance = Service_category.objects.filter( Q(status_history__status_date__month=main_date))
        # else:
            # fresh_assigned_intance = Service_category.objects.filter(created_date__range=[start_date, last_date])
            # open_leads_intance = Service_category.objects.filter(Q(status_history__status_date__range = [start_date, last_date]))
        # print('open_leads_intance',len(fresh_assigned_intance))
        if date_type == 'this_month' or date_type == 'last_month':
            leadsData = ServiceCategory.objects.filter(created_date__month=main_date, assigned_manager=request.user)
            # pitch_in_progress = ServiceCategory.objects.filter( Q(status_history__status_date__month=main_date), Q(status_history__status__title='pitch in progress') )
            all_leads = ServiceCategory.objects.filter(assigned_manager=request.user)
            for al in all_leads:
                if al.status_history.filter( Q(status_date__month=main_date)).order_by('-id').first():
                    primary_data.append({'lead_id': al, 'status': al.status_history.filter( Q(status_date__month=main_date)).order_by('-id').first().status.title })
        else:
            leadsData = ServiceCategory.objects.filter(created_date__range=[start_date, last_date], assigned_manager=request.user)
            all_leads = ServiceCategory.objects.filter(assigned_manager=request.user)
            for al in all_leads:
                if al.status_history.filter( Q(status_date__range=[start_date, last_date])).order_by('-id').first() != None:
                    primary_data.append({'lead_id': al, 'status': al.status_history.filter( Q(status_date__range=[start_date, last_date])).order_by('-id').first().status.title })
        def associate_performance():
            def associate_performance_fun(data, lead_id):
                if lead_id.status_history.all().order_by('-id').first().status.title == 'subscription_started':
                    data['subscription_started'].append(lead_id)
                elif lead_id.status_history.all().order_by('-id').first().status.title == 'follow_up_unresponsive':
                    data['follow_up_unresponsive'].append(lead_id)
                elif lead_id.status_history.all().order_by('-id').first().status.title == 'not_interested':
                    data['not_interested'].append(lead_id)
                else:
                    data['open'].append(lead_id)
                data['assigned'].append(lead_id)
                data['name'] = (lead_id.associate)
            def associate_performance_append_fun(secondary_data):
                if len(secondary_data) != 0:
                    for o in secondary_data:
                        if o['name'] == m['lead_id'].associate:
                            associate_performance_fun(o, m['lead_id'])
                            break
                    else:
                        if o['name'] != m['lead_id'].associate:
                            print('working once')
                            associate_performance_fun(scr_data, m['lead_id'])
                            secondary_data.append(scr_data)
                else:
                    associate_performance_fun(scr_data, m['lead_id'])
                    secondary_data.append(scr_data)
            for m in primary_data:
                scr_data = { 'name': '',  "assigned": [], 'open': [], 'subscription_started': [], 'follow_up_unresponsive': [], 'not_interested': [] }
                if date_type == 'this_month' or date_type == 'last_month':
                    if m['lead_id'].created_date.month == main_date:
                        if m['lead_id'].associate !=None :
                            associate_performance_append_fun(secondary_data)
                else:
                    if start_date <= m['lead_id'].created_date.date() <= last_date:
                        if m['lead_id'].associate !=None :
                            associate_performance_append_fun(secondary_data)
        if data_type == 'overall_performance':
            associate_performance()
            main_data = secondary_data
            secondary_data = []
            def dataShift(sd, scr):
                for asng in sd['assigned']:
                    scr['assigned'].append(asng)
                for asng in sd['open']:
                    scr['open'].append(asng)
                for asng in sd['subscription_started']:
                    scr['subscription_started'].append(asng)
                for asng in sd['follow_up_unresponsive']:
                    scr['follow_up_unresponsive'].append(asng)
                for asng in sd['not_interested']:
                    scr['not_interested'].append(asng)
            for sd in main_data:
                scr_data = {'name': '', 'assigned': [], 'open': [], 'subscription_started': [], 'follow_up_unresponsive': [], 'not_interested': []}
                if len(secondary_data) != 0:
                    for scr in secondary_data:
                        if scr['name'] == sd['name'].reporting_manager:
                            dataShift(sd, scr)
                            # secondary_data.append(scr)
                            break
                    else:
                        # if scr['name'] != sd['name'].reporting_manager:
                        scr_data['name'] = sd['name'].reporting_manager
                        dataShift(sd, scr_data)
                        secondary_data.append(scr_data)
                        break
                else:
                    scr_data['name'] = sd['name'].reporting_manager
                    dataShift(sd, scr_data)
                    secondary_data.append(scr_data)
        elif data_type == 'associate_level_performance':
            associate_performance()
        elif data_type == 'service_level_performance':
            def dataShift(sd, scr):
                scr['assigned'].append(sd)
                lead_status = sd.status_history.filter( Q(status_date__month=main_date)).order_by('-id').first().status.title
                if lead_status == 'subscription_started':
                    scr['subscription_started'].append(sd)
                elif lead_status == 'follow_up_unresponsive':
                    scr['follow_up_unresponsive'].append(sd)
                elif lead_status == 'not_interested':
                    scr['not_interested'].append(sd)
                else:
                    scr['open_leads'].append(sd)
            for sd in leadsData:
                scr_data = {'marketplace': '', 'service': '', 'assigned': [], 'open_leads': [], 'subscription_started': [], 'follow_up_unresponsive': [], 'not_interested': []}
                for scr in secondary_data:
                    print('working 1', scr)
                    if scr['marketplace'] == sd.service.marketplace and scr['service'] == sd.service.service:
                        dataShift(sd, scr)
                        break
                else:
                    scr_data['marketplace'] = sd.service.marketplace
                    scr_data['service'] = sd.service.service
                    dataShift(sd, scr_data)
                    secondary_data.append(scr_data)
        # leadsData = Service_category.objects.select_related().filter()
    elif request.user.user_role.filter(title='business_development_associate').exists():
        if date_type == 'this_month' or date_type == 'last_month':
            leadsData = ServiceCategory.objects.filter(created_date__month=main_date, associate=request.user)
            # pitch_in_progress = ServiceCategory.objects.filter( Q(status_history__status_date__month=main_date), Q(status_history__status__title='pitch in progress') )
            all_leads = ServiceCategory.objects.filter(associate=request.user)
            for al in all_leads:
                if al.status_history.filter( Q(status_date__month=main_date)).order_by('-id').first():
                    primary_data.append({'lead_id': al, 'status': al.status_history.filter( Q(status_date__month=main_date)).order_by('-id').first().status.title })
        else:
            leadsData = ServiceCategory.objects.filter(created_date__range=[start_date, last_date], associate=request.user)
            all_leads = ServiceCategory.objects.filter(associate=request.user)
            for al in all_leads:
                if al.status_history.filter( Q(status_date__range=[start_date, last_date])).order_by('-id').first() != None:
                    primary_data.append({'lead_id': al, 'status': al.status_histqory_all.filter( Q(status_date__range=[start_date, last_date])).order_by('-id').first().status.title })
        def associate_performance():
            def associate_performance_fun(data, lead_id):
                if lead_id.status_history.all().order_by('-id').first().status.title == 'subscription_started':
                    data['subscription_started'].append(lead_id)
                elif lead_id.status_history.all().order_by('-id').first().status.title == 'follow_up_unresponsive':
                    data['follow_up_unresponsive'].append(lead_id)
                elif lead_id.status_history.all().order_by('-id').first().status.title == 'not_interested':
                    data['not_interested'].append(lead_id)
                else:
                    data['open'].append(lead_id)
                data['assigned'].append(lead_id)
                data['name'] = (lead_id.associate)
            def associate_performance_append_fun(secondary_data):
                if len(secondary_data) != 0:
                    for o in secondary_data:
                        if o['name'] == m['lead_id'].associate:
                            associate_performance_fun(o, m['lead_id'])
                            break
                    else:
                        if o['name'] != m['lead_id'].associate:
                            print('working once')
                            associate_performance_fun(scr_data, m['lead_id'])
                            secondary_data.append(scr_data)
                else:
                    associate_performance_fun(scr_data, m['lead_id'])
                    secondary_data.append(scr_data)
            for m in primary_data:
                scr_data = { 'name': '',  "assigned": [], 'open': [], 'subscription_started': [], 'follow_up_unresponsive': [], 'not_interested': [] }
                if date_type == 'this_month' or date_type == 'last_month':
                    if m['lead_id'].created_date.month == main_date:
                        if m['lead_id'].associate !=None :
                            associate_performance_append_fun(secondary_data)
                else:
                    if start_date <= m['lead_id'].created_date.date() <= last_date:
                        if m['lead_id'].associate !=None :
                            associate_performance_append_fun(secondary_data)
        if data_type == 'overall_performance':
            associate_performance()
            main_data = secondary_data
            secondary_data = []
            def dataShift(sd, scr):
                for asng in sd['assigned']:
                    scr['assigned'].append(asng)
                for asng in sd['open']:
                    scr['open'].append(asng)
                for asng in sd['subscription_started']:
                    scr['subscription_started'].append(asng)
                for asng in sd['follow_up_unresponsive']:
                    scr['follow_up_unresponsive'].append(asng)
                for asng in sd['not_interested']:
                    scr['not_interested'].append(asng)
            for sd in main_data:
                scr_data = {'name': '', 'assigned': [], 'open': [], 'subscription_started': [], 'follow_up_unresponsive': [], 'not_interested': []}
                if len(secondary_data) != 0:
                    for scr in secondary_data:
                        if scr['name'] == sd['name'].reporting_manager:
                            dataShift(sd, scr)
                            # secondary_data.append(scr)
                            break
                    else:
                        # if scr['name'] != sd['name'].reporting_manager:
                        scr_data['name'] = sd['name'].reporting_manager
                        dataShift(sd, scr_data)
                        secondary_data.append(scr_data)
                        break
                else:
                    scr_data['name'] = sd['name'].reporting_manager
                    dataShift(sd, scr_data)
                    secondary_data.append(scr_data)
        elif data_type == 'associate_level_performance':
            associate_performance()
        elif data_type == 'service_level_performance':
            def dataShift(sd, scr):
                scr['assigned'].append(sd)
                lead_status = sd.status_history.filter( Q(status_date__month=main_date)).order_by('-id').first().status.title
                if lead_status == 'subscription_started':
                    scr['subscription_started'].append(sd)
                elif lead_status == 'follow_up_unresponsive':
                    scr['follow_up_unresponsive'].append(sd)
                elif lead_status == 'not_interested':
                    scr['not_interested'].append(sd)
                else:
                    scr['open_leads'].append(sd)
            for sd in leadsData:
                scr_data = {'marketplace': '', 'service': '', 'assigned': [], 'open_leads': [], 'subscription_started': [], 'follow_up_unresponsive': [], 'not_interested': []}
                for scr in secondary_data:
                    print('working 1', scr)
                    if scr['marketplace'] == sd.service.marketplace and scr['service'] == sd.service.service:
                        dataShift(sd, scr)
                        break
                else:
                    scr_data['marketplace'] = sd.service.marketplace
                    scr_data['service'] = sd.service.service
                    dataShift(sd, scr_data)
                    secondary_data.append(scr_data)
        # leadsData = Service_category.objects.select_related().filter()
        # leadsData = Service_category.objects.select_related().filter(associate=request.user)

    elif request.user.user_role.filter(title='admin').exists():
        # if request.user.designation.title == 'lead_manager':
        lead_instance = Leads.objects.select_related().filter(visibility=True)
        leadsData = []
        for ld in lead_instance:
            for sc in ld.service_category.all():
                leadsData.append(sc)

        #     print('leadsData',leadsData)
        # elif request.user.designation.title == 'user_manager':
        #     leadsData=UserAccount.objects.filter(visibility=True)

    elif request.user.user_role.filter(title='accounts_team_lead').exists():
        leadsData = ServiceCategory.objects.select_related().filter(status_history__status__title = 'validation_pending')



    assigned_leads = len(leadsData)

    # if request.user.department.title == 'admin' and request.user.designation.title == 'user_manager':
    #       total_employees = leadsData
    #       active = [ ld for ld in leadsData if ld.employee_status.title == 'active']
    #       unplanned_leave = [ ld for ld in leadsData if ld.employee_status.title == 'on unplanned leave']
    #       planned_leave = [ ld for ld in leadsData if ld.employee_status.title == 'on planned leave']
    #       absconded = [ ld for ld in leadsData if ld.employee_status.title == 'absconded']
    #       notice_period = [ ld for ld in leadsData if ld.employee_status.title == 'on notice period']
    #       resigned = [ ld for ld in leadsData if ld.employee_status.title == 'resigned']

    #       context = {'total_employees': total_employees, 'active': active, 'unplanned_leave': unplanned_leave, 'planned_leave': planned_leave, 'absconded': absconded, 'notice_period': notice_period, 'resigned': resigned }

    if request.user.user_role.filter(title='accounts_team_lead').exists() or request.user.user_role.filter(title='accounts_associate').exists():

        context = {}
        
        context['approved'] = leadsData
        context['approved'] = [ ld.commercial_approval for ld in leadsData if ld.commercial_approval != None if ld.commercial_approval.status.title == 'approved'  ]
        context['rejected'] = [ ld.commercial_approval for ld in leadsData if ld.commercial_approval != None if ld.commercial_approval.status.title == 'rejected'  ]

        # context = {'payment_requests': leadsData, 'approved': approved, 'rejected': rejected}



    else:
        # print('primary_data',primary_data)
        yet_to_contact = [m['lead_id'] for m in primary_data if m['status'] == 'yet_to_contact' ]
        pitch_in_progress = [m['lead_id'] for m in primary_data if m['status'] == 'pitch_in_progress' ]
        proposal_email_sent = [m['lead_id'] for m in primary_data if m['status'] == 'follow_up_proposal_sent' ]
        follow_up = [m['lead_id'] for m in primary_data if m['status'] == 'follow_up' ]
        # mou_generated = [m['lead_id'] for m in primary_data if m['status'] == 'mou generated' ]
        # pending_for_mou_validation = [m['lead_id'] for m in primary_data if m['status'] == 'mou_pending validation' ]
        pending_for_commercial_approval = [m['lead_id'] for m in primary_data if m['status'] == 'commercial_approval_pending' ]
        commercial_rejected = [ m['lead_id'] for m in primary_data if m['status'] == 'commercial_rejected' ]
        converted_leads = [ m['lead_id'] for m in primary_data if m['status'] == 'subscription_started' ] 
        pending_for_mou = [ m['lead_id'] for m in primary_data if m['status'] == 'follow_up_mou_pending' ] 
        pending_for_payment = [ m['lead_id'] for m in primary_data if m['status'] == 'payment_pending' ] 
        payment_validation_pending = [ m['lead_id'] for m in primary_data if m['status'] == 'validation_pending' ] 
        follow_up_unresponsive = [ m['lead_id'] for m in primary_data if m['status'] == 'follow_up_unresponsive' ] 
        not_interested = [ m['lead_id'] for m in primary_data if m['status'] == 'not_interested' ] 
        assign_service_associate_pending = [ m['lead_id'] for m in primary_data if m['status'] == 'assign_associate_pending' ]

        context = {'assigned_leads': assigned_leads, 'pitch_in_progress': pitch_in_progress, 'converted_leads': converted_leads, 'pending_for_mou': pending_for_mou, 'pending_for_payment': pending_for_payment, 'payment_validation_pending': payment_validation_pending, 'follow_up_unresponsive': follow_up_unresponsive, 'not_interested': not_interested, 'yet_to_contact': yet_to_contact, 'assign_service_associate_pending': assign_service_associate_pending,
        'proposal_email_sent': proposal_email_sent, 'follow_up': follow_up, 'pending_for_commercial_approval': pending_for_commercial_approval, 'commercial_rejected': commercial_rejected, 'primary_data': primary_data, 'secondary_data':secondary_data}

    return HttpResponse(render(request, 'dashboard.html', context ))


@login_required(login_url='/login')
def usersFun(request):

    if request.GET.get('page'):
        page = request.GET.get('page')
    else:
        page=1
        type='active'
    
    if request.GET.get('type'):
        type = request.GET.get('type')
    else:
        type='active'

    
    if request.user.user_role.filter(title='super_admin').exists() or request.user.user_role.filter(title='admin') or request.user.is_admin :

        if type == 'active':
            users = UserAccount.objects.filter(visibility=True)
        elif type == 'archive' :
            users = UserAccount.objects.filter(visibility=False)


        # count = math.ceil(UserAccount.objects.filter(visibility=visibility).count() / 10)
        p = Paginator(users, 20)
        data = p.page(page)
            
            # if users.exists():
                # data = viewUserDictDataStructure(users)
  
                # serializer = viewUserSerializer(data=data, many=True)
                # serializer.is_valid(raise_exception=True)
                # res = resFun(status.HTTP_200_OK, 'request successful', {"data": serializer.data, 'current_page': page, 'total_pages': count})

            # else:
                # res = resFun(status.HTTP_200_OK, 'no data found', {'data': [], 'current_page': page, 'total_pages': count} )
        # else:
            # res = resFun(status.HTTP_400_BAD_REQUEST, 'you are not authorized to view this data', [] )


        # service_object = Services_and_Commercials.objects.all()
        # print('service_object',service_object)
        # segment = [ so.segment for so in service_object if so.segment != None ]
        # service = [ so.service for so in service_object if so.service != None]
        # marketplace = [ so.marketplace for so in service_object if so.service != None ]
        # program = [ so.program for so in service_object]
        # sub_program = [ so.sub_program for so in service_object if so.sub_program !=None ]

        user_role = UserRole.objects.all()
        employee_status = EmployeeStatus.objects.all()
        # director = UserAccount.objects.filter(department__title='director')
        # user_manager = UserAccount.objects.filter(designation__title='user_manager')
        # lead_manager = UserAccount.objects.filter(designation__title='lead_manager')
        # team_leader = UserAccount.objects.filter(designation__title='team_leader')


        def removeDuplicate_DICT(array, first_value, second_value):
            unique_set = set()
            unique_list = []

            for s in array:
                # tupple_instance =   tuple(sorted(s.items()))
                identifier = (s[first_value], s[second_value])
                # print(identifier, unique_set)
                if identifier not in unique_set:
                    unique_set.add(identifier)
                    unique_list.append(s)
            return unique_list


        # service_list_unfiltered = []
        # marketplace_list_unfiltered = []
        lead_filter_tabs = [ 'all', 'yet_to_contact', 'pitch_in_progress', 'follow_up', 'payment_pending', 'validation_pending', 'assign_associate_pending', 'not_interested', 'dead_lead', 'subscription_started'  ]

        # service_list = removeDuplicate_DICT(service_list_unfiltered, 'segment', 'service')
        # marketplace_list = removeDuplicate_DICT(marketplace_list_unfiltered, 'service', 'marketplace')


        # print('marketplace_list',marketplace_list)


        segment_data = Segment.objects.filter(visibility=True)
        service_data = Service.objects.filter(visibility=True)
        marketplace_data = Marketplace.objects.filter(visibility=True)
        program_data = Program.objects.filter(visibility=True)

        # segment_data = Segment.objects.filter(visibility=True)
        # service_data = Service.objects.filter(visibility=True)
        # marketplace_data = Marketplace.objects.filter(visibility=True)
        # program_data = Program.objects.filter(visibility=True)

        return HttpResponse(render(request, 'users.html', context={'data':data, 'program': program_data, 'current_page': page, 'dropdown_data': [{'segment' : segment_data, 'service' : service_data, 'marketplace' : marketplace_data, 'program' : program_data}], 'user_role': user_role, 'employee_status': employee_status,  }))
    else:
        messages.success(request, 'you are not authorized for this action!')
        return HttpResponse(render(request, 'users.html'))


@login_required(login_url='/login')
def servicesFun(request):

    # try:
    #     type = request.GET.get('type')
    #     if type == None:
    #         type = 'commercials'
    # except:
    #     type = 'commercials'

    try:
        segment = request.GET.get('segment')
        if segment == None:
            segment = 'active'
    except:
        segment = 'active'

    try:
        page = request.GET.get('page')
        if page == None:
            page = 1
    except:
        page = 1

    paid_by = PaidBy.objects.all()
    payment_model = PaymentModel.objects.all()
    payment_terms = PaymentTerms.objects.all()
    

    # if type == 'commercials':

    #     if segment == 'active':
    #         if (request.user.department.title == 'director'):
    #             service_commercials = Services_and_Commercials.objects.filter(program__visibility=True, visibility=True)
    #             print('service_commercials',service_commercials)

    #     elif segment == 'archive':
    #         service_commercials = Services_and_Commercials.objects.filter(visibility=False)

    #     p = Paginator(service_commercials, 10)
    #     data = p.page(page)

    #     segment_data = Segment.objects.filter(visibility=True)
    #     service_data = Service.objects.filter(visibility=True)
    #     marketplace_data = Marketplace.objects.filter(visibility=True)
    #     program_data = Program.objects.filter(visibility=True)
    #     # sub_program_data = Sub_Program.objects.filter(visibility=True)

    #     # Services_and_Commercials.objects.filter('')

    #     return HttpResponse(render(request, 'services.html', context={'content': data ,'current_page' : page, 'segment': segment_data,'service': service_data, 'marketplace': marketplace_data, 'program': program_data,
    #                                                                 #    'sub_program': sub_program_data,
    #                                 'data': [{'segment' : segment_data, 'service' : service_data, 'marketplace' : marketplace_data, 'program' : program_data, 
    #     # 'sub_program' : sub_program_data
    #     }], 'payment_model': payment_model, 'paid_by': paid_by } ))

    # elif type == 'manage_service':

    try:
        service = request.GET.get('service')
        if service == None:
            service = 'active'
    except:
        service = 'active'
    try:
        marketplace = request.GET.get('marketplace')
        if marketplace == None:
            marketplace = 'active'
    except:
        marketplace = 'active'
    try:
        program = request.GET.get('program')
        if program == None:
            program = 'active'
    except:
        program = 'active'
    # try:
    #     sub_program = request.GET.get('sub_program')
    #     if sub_program == None:
    #         sub_program = 'active'
    # except:
    #     sub_program = 'active'
    if segment == 'active':
        segment_data = Segment.objects.filter(visibility=True)
    elif segment == 'archive':
        segment_data = Segment.objects.filter(visibility=False)
    if service == 'active':
        service_data = Service.objects.filter(visibility=True)
    elif service == 'archive':
        service_data = Service.objects.filter(visibility=False)
    if marketplace == 'active':
        marketplace_data = Marketplace.objects.filter(visibility=True)
    elif marketplace == 'archive':
        marketplace_data = Marketplace.objects.filter(visibility=False)
    if program == 'active':
        program_data = Program.objects.filter(visibility=True)
    elif program == 'archive':
        program_data = Program.objects.filter(visibility=False)
        
    # if sub_program == 'active':
    #     sub_program_data = Sub_Program.objects.filter(visibility=True)
    # elif sub_program == 'archive':
    #     sub_program_data = Sub_Program.objects.filter(visibility=False)
    return HttpResponse(render(request, 'services.html', context={'segment' : segment_data, 'service' : service_data, 'marketplace' : marketplace_data, 'program' : program_data,  'data': [{'segment' : segment_data, 'service' : service_data, 'marketplace' : marketplace_data, 'program' : program_data}], 'payment_model': payment_model, 'payment_terms': payment_terms, 'paid_by': paid_by }))




@login_required(login_url='/login')
def approvalsFun(request):

    if request.GET.get('page'):
        page = request.GET.get('page')
    else:
        page=1
    
    if request.GET.get('type'):
        type = request.GET.get('type')
    else:
        type='leaves'

    print('type', type)


    if roleCheck(request.user,'super_admin'):
        if type == 'leaves':
            # leadsData = [{}]
            client_turnover = []
            business_category = []
            leadsData = EmployeeLeaves.objects.filter(status__title='pending')
            
            # pass
        else:

            client_turnover = ClientTurnover.objects.all()
            business_category = BusinessCategory.objects.all()

            leadsData = Leads.objects.prefetch_related('service_category__commercial_approval').filter(Q(service_category__commercial_approval__isnull=False) & Q(service_category__commercial_approval__approval_type__title=type) & Q(visibility = True)).exclude(Q(service_category__commercial_approval__status__title='approved') | Q(service_category__commercial_approval__status__title='rejected') ).all()
        p = Paginator(leadsData, 10)
        data = p.page(page)

        if not len(data) > 0:
            data = 'no data'

        return HttpResponse(render(request, 'approval.html', context={'data': data, 'current_page': page, 'client_turnover': client_turnover, 'business_category': business_category } ))

    elif roleCheck(request.user,'business_development_team_lead'):
        employee_leave_instance = EmployeeLeaves.objects.filter(status__title='pending', employee__reporting_manager=request.user)
        if len(employee_leave_instance) > 0:
            p = Paginator(employee_leave_instance, 10)
            data = p.page(page)
        else:
            data = 'no data'
        return HttpResponse(render(request, 'approval.html', context={'data': data, 'current_page': page }))
    else:
        messages.success(request, 'you are not authorized for this action!')
        return HttpResponse(render(request, 'approval.html', context={'data':"no data"}))




@login_required(login_url='/login')
def paymentsFun(request):
    try:
        if request.GET.get('page'):
            page = int(request.GET.get('page'))
        else:
            page=1
    except:
        page=1

    limit = 10
    offset = (page - 1) * limit

    # latest_status = Status_history.objects.filter(service_category= OuterRef('pk')).order_by('-id').values('status__title')
    # leadsData = Service_category.objects.annotate(latest_status_title=Subquery(latest_status)).order_by('id').filter(latest_status_title = 'payment_validation_pending')

    subquery = Subquery(StatusHistory.objects.filter(service_category=OuterRef('service_category__pk')).order_by('-id').values('status__title')[:1])
    # leadsData = Service_category.objects.annotate(last_status_title = subquery).filter(last_status_title='payment_validation_pending')
    leadsData = Leads.objects.annotate(service_category__last_status_title = subquery).filter( service_category__last_status_title = 'payment_validation_pending')

    print('leadsData',leadsData)

    p = Paginator(leadsData, 10)
    data = p.page(page)


    return HttpResponse(render(request, 'payments.html', context = { 'data': data, 'current_page': page }))





def leadFilterFunction(data):
    trial_list = []
    
    if not data['lead_status'] == 'all':
    # leadsData = Leads.objects.select_related().filter()

        if 'follow_up' in data['lead_status']:
            service_category_instance =  ServiceCategory.objects.filter(status_history__status__title__icontains='follow_up')
        

            # status_instance =  Status_history.objects.filter().values('service_category', 'status', 'id').order_by('-id')
        service_category_instance =  ServiceCategory.objects.filter(status_history__status__title__in = data['lead_status'])

        for s in service_category_instance:
            status_instance = s.status_history.all().order_by('-id').first().status.title
            for d in data['lead_status']:
                if d in status_instance:
                    trial_list.append(s.id)

    return trial_list






@login_required(login_url='/login')
def leadsFun(request):
    try: 
        if request.GET.get('page'):
            page = int(request.GET.get('page'))
        else:
            page = 1
    except:
        page=1

    try:
        if request.GET.get('type'):
            type = request.GET.get('type')
        else:
            type = 'active'
    except:
        type = 'active'

    try:
        if request.GET.get('lead_status'):
            lead_status = request.GET.get('lead_status').split('%2C')
        else:
            lead_status = []
    except:
        lead_status = []

    try:
        if request.GET.get('associate'):
            associate_filter_list = request.GET.get('associate').split('%2C')
        else:
            associate_filter_list = []
    except:
        associate_filter_list = []
    
    try:
        if request.GET.get('lead_assigned'):
            lead_assigned_filter_list = request.GET.get('lead_assigned').split('%2C')
        else:
            lead_assigned_filter_list = []
    except:
        lead_assigned_filter_list = []
    
    try:
        if request.GET.get('segment'):
            segment_filter_list = request.GET.get('segment').split('%2C')
        else:
            segment_filter_list = []
    except:
        segment_filter_list = []

    try:
        if request.GET.get('service'):
            service_filter_list = request.GET.get('service').split('%2C')
        else:
            service_filter_list = []
    except:
        service_filter_list = []

    try:
        if request.GET.get('marketplace'):
            marketplace_filter_list = request.GET.get('marketplace').split('%2C')
        else:
            marketplace_filter_list = []
    except:
        marketplace_filter_list = []

    try:
        if request.GET.get('program'):
            program_filter_list = request.GET.get('program').split('%2C')
        else:
            program_filter_list = []
    except:
        program_filter_list = []

    try:
        if request.GET.get('rs'):
            limit = int(request.GET.get('rs'))
        else:
            limit = 25
    except:
        limit = 25



    user = request.user
    # limit = 10
    offset = int((page - 1) * limit)
    data = []
    pagecount = 1

    # service_object = Services_and_Commercials.objects.all()
    # segment = set([ so.segment for so in service_object if so.segment != None])
    # service = set([ so.service for so in service_object])
    # marketplace = set([ so.marketplace for so in service_object])
    # program = set([so.program for so in service_object])
    # sub_program = set([ so.sub_program for so in service_object if so.sub_program !=None ])
    client_turnover = ClientTurnover.objects.all()
    business_category = BusinessCategory.objects.all()
    country_code = CountryCode.objects.all()


    def removeDuplicate_DICT(array, first_value, second_value):
        unique_set = set()
        unique_list = []
    
        for s in array:
            # tupple_instance =   tuple(sorted(s.items()))
            identifier = (s[first_value], s[second_value])
            # print(identifier, unique_set)
            if identifier not in unique_set:
                unique_set.add(identifier)
                unique_list.append(s)
        return unique_list


    # for so in service_object:
    #     print(so, so.program)


    lead_status_tabs = [ 'all', 'yet_to_contact', 'pitch_in_progress', 'follow_up', 'payment_pending', 'validation_pending', 'assign_associate_pending', 'not_interested', 'dead_lead', 'subscription_started'  ]


    if type == 'active':
        client_id_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('client_id')[:1])
        client_name_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('client_name')[:1])
        contact_number_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('contact_number')[:1])
        alternate_contact_number_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('alternate_contact_number')[:1])
        email_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('email_id')[:1])
        alternate_email_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('alternate_email_id')[:1])
        hot_lead_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('hot_lead')[:1])
        request_id_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('request_id')[:1])
        provider_id_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('provider_id')[:1])
        requester_id_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('requester_id')[:1])
        requester_location_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('requester_location')[:1])
        business_name_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('business_name')[:1])
        requester_sell_in_country_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('requester_sell_in_country')[:1])
        gst_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('gst')[:1])
        service_requester_type_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('service_requester_type')[:1])
        upload_date_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('upload_date')[:1])
        business_category_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('business_category')[:1])
        client_turnover_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('client_turnover')[:1])
        brand_name_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('brand_name')[:1])
        seller_address_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('seller_address')[:1])
        lead_owner_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('lead_owner')[:1])
        contact_preferences_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('contact_preferences')[:1])
        firm_type_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('firm_type')[:1])
        business_type_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('business_type')[:1])
        client_designation_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('client_designation')[:1])
        # Subquery to get the latest status title for each Service_category
        latest_status_subquery = Subquery(StatusHistory.objects.filter(service_category=OuterRef('pk')).order_by('-id').values('status__title')[:1])
  
        query = Q()
        query_program = Q()
        query_marketplace = Q()
        query_service = Q()
        query_segment = Q()
        exclude_query = Q()
        user_query = Q()
        # user_filter_query = Q()

        if len(lead_status) > 0:
            for status in lead_status:
                query |= Q(last_status_title__icontains=status)
        
        print('associate_list', associate_filter_list)
        if len(associate_filter_list) > 0:
            print('associate list working')
            for associate in associate_filter_list:
                query |= Q(associate=associate)
        
        if len(lead_assigned_filter_list) > 0:
            for lead_assigned in lead_assigned_filter_list:
                if lead_assigned == 'assigned':
                    exclude_query |= Q(associate=None)
                elif lead_assigned == 'unassigned':
                    query |= Q(associate=None)
        if len(segment_filter_list) > 0:
            for segment in segment_filter_list:
                    query_segment |= Q(program__marketplace__service__segment=segment)
        if len(service_filter_list) > 0:
            for service in service_filter_list:
                    query_service |= Q(program__marketplace__service=service)
        if len(marketplace_filter_list) > 0:
            for marketplace in marketplace_filter_list:
                    query_marketplace |= Q(program__marketplace=marketplace)
        if len(program_filter_list) > 0:
            for program in program_filter_list:
                    query_program |= Q(program=program)
                    
        if roleCheck(user,'super_admin') or roleCheck(user,'admin') or request.user.is_admin:
            pass
        elif roleCheck(user,'business_development_team_lead'):
            # user_query |= Q(program__in= user.program.all())
            team_members = list(UserAccount.objects.filter(reporting_manager=request.user).values_list('id', flat=True ))
            print('team_members', team_members )
            user_query |= Q(associate= user)
            user_query |= Q(associate__in= team_members)
            # associate |= Q(service__program__in= user.program.all())
        elif roleCheck(user,'business_development_associate'):
            # print(user.program.all())
            # user_query |= Q(program__in= user.program.all())
            user_query |= Q(associate= user)
    
                            
        leadsData = ServiceCategory.objects.annotate(
            client_id=client_id_subquery, 
            client_name=client_name_subquery, 
            contact_number=contact_number_subquery, 
            alternate_contact_number=alternate_contact_number_subquery, 
            email_id=email_subquery,
            alternate_email_id=alternate_email_subquery,
            hot_lead = hot_lead_subquery,
            request_id = request_id_subquery,
            provider_id = provider_id_subquery,
            requester_id = requester_id_subquery,
            requester_location = requester_location_subquery,
            business_name = business_name_subquery,
            requester_sell_in_country = requester_sell_in_country_subquery,
            gst = gst_subquery,
            service_requester_type = service_requester_type_subquery,
            upload_date = upload_date_subquery,
            business_category = business_category_subquery,
            client_turnover = client_turnover_subquery,
            lead_owner = lead_owner_subquery,
            brand_name = brand_name_subquery,
            seller_address = seller_address_subquery,

            contact_preferences = contact_preferences_subquery,
            firm_type = firm_type_subquery,
            business_type = business_type_subquery,
            client_designation = client_designation_subquery,

            last_status_title=latest_status_subquery
        ).filter(query).filter(query_program).filter(query_marketplace).filter(query_service).filter(query_segment).filter(user_query).exclude(exclude_query).order_by('-id').order_by('-hot_lead')

        print('leadsData', leadsData)

    elif type == 'archive':

        visibility_subquery = Subquery(Leads.objects.filter(service_category=OuterRef('pk')).values('visibility')[:1])

        leadsData = ServiceCategory.objects.annotate(visibility = visibility_subquery ).filter(visibility = False)


    if leadsData != None:
        p = Paginator(leadsData, limit)
        data = p.page(page)
    else:
        data = None

    segment_data = Segment.objects.filter(visibility=True)
    service_data = Service.objects.filter(visibility=True)
    marketplace_data = Marketplace.objects.filter(visibility=True)
    program_data = Program.objects.filter(visibility=True)

    
    context = {'data': data, 'current_page': page,
                # 'sub_program': sub_program, 
               'client_turnover': client_turnover, 'business_category': business_category, 'country_code': country_code, 'lead_status': lead_status_tabs, 'dropdown_data': [{'segment' : segment_data, 'service' : service_data, 'marketplace' : marketplace_data, 'program' : program_data, 
        # 'sub_program' : sub_program_data
        }]}

    # return HttpResponse(render(request, 'leads.html', context ))
    return HttpResponse(render(request, 'leads.html', context ))



@login_required(login_url='/login')
def createUserAccountFun(request):
    print('this works')
    # for r,v in request.POST.items():
        # print(r,v)
    data = {}

    # data['segment'] = request.POST.get('segment')
    # data['director'] = request.POST.get('director')
    # data['user_manager'] = request.POST.get('user_manager')
    # data['lead_manager'] = request.POST.get('lead_manager')
    # data['team_leader'] = request.POST.get('team_leader')
    # data['service'] = request.POST.getlist('service')
    # data['marketplace'] =request.POST.getlist('marketplace')
    data['program'] =request.POST.getlist('program')
    # data['sub_program'] =request.POST.getlist('sub_program')
    serv_items = ['service', 'marketplace', 'program']
    for k,v in request.POST.items():
        if not k in serv_items:
            if k == 'designation':
                data[k] = None if v == 'null' else v
            else:
                data[k] = v
                
    if roleCheck(request.user,'super_admin'):
        print('data',data)
        serializer = AdminRegistrationSerializer(data=data)
    elif roleCheck(request.user,'admin'):
        serializer = LeadManagerRegistrationSerializer(data=data)
        # serializer = AdminRegistrationSerializer(data=data)


    if serializer.is_valid():
        instance = serializer.save()
        instance.created_by = request.user
        instance.save()
        
        ua_ser = UserAccount.objects.filter(email=serializer.data['email']).first()
        message = CannedEmail.objects.get(email_type = 'welcome_email')
        message = message.email
        message = str(message).replace("{{{link}}}", f'<a href="https://lms-backend-ren.onrender.com/account/generate_password/{ua_ser.pk}/{ua_ser.user_pwd_token}">fill more details</a>')
        email_id = ua_ser.email
        subject = 'Welcome to Evitamin!'
        from_email = 'akshatnigamcfl@gmail.com'
        recipient_list = [email_id]
        text = 'email sent from MyDjango'
        # if send_mail(subject, message, from_email, recipient_list):
        email = EmailMultiAlternatives(subject, text, from_email, recipient_list)
        email.attach_alternative(message, 'text/html')
        # email.attach_file('files/uploadFile_0dTGU7A.csv', 'text/csv')
        email.send()
        
        #welcome email to the user, authentication
        messages.success(request, 'registration successful!')
        return redirect(usersFun)
        # res = resFun(status.HTTP_200_OK,'registration successful',serializer.data)
    else:
        print(serializer.errors)
        messages.error(request, 'registration failed!')
        return redirect(usersFun)



@login_required(login_url='/login')
def updateUserAccountFun(request):
    for r in request.POST.items():
        print('r',r)

    employee_id = request.POST.get('employee_id')
    user_instance = UserAccount.objects.filter(employee_id=employee_id)
    if user_instance.exists():
        user_instance
        serializer = UpdateUserSerializer(user_instance.first(), data=request.POST, partial=True )
        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'update successful')
            return redirect(usersFun)            
        else:
            messages.error(request, 'something went wrong')
            return redirect(usersFun)

    else:
        messages.error(request, 'user not found or invalid employee id!')
        return redirect(usersFun)



@login_required(login_url='/login')
def archiveUserFun(request):
    
    user_id = request.GET.get('user_id')
    user = UserAccount.objects.get(id=user_id)
    if user:
        user.visibility = False
        user.save()

        return HttpResponseRedirect(reverse(usersFun))
        # return HttpResponse(render(request, 'users.html', context={'data':"no data", 'message': "user archived" } ))
    else:
        return HttpResponseRedirect(reverse(usersFun))
        # return HttpResponse(render(request, 'users.html', context={'data':"no data", 'message': "invalid user id" } ))


@login_required(login_url='/login')
def restoreUserFun(request):
    
    user_id = request.GET.get('user_id')
    user = UserAccount.objects.get(id=user_id)
    if user:
        user.visibility = True
        user.save()
        return HttpResponseRedirect(reverse(usersFun))
    else:
        return HttpResponseRedirect(reverse(usersFun))



