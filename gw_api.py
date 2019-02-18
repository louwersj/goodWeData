import json
import logging
import time
from datetime import datetime, timedelta
import requests

''' this work is based upon the groundwork done by Mark Ruys on his original GW_API '''
__author__ = "Johan Louwers"
__copyright__ = "Copyright 2019, Johan Louwers"
__license__ = "MIT"
__email__ = "louwersj@gmail.com"


class GoodWeApi:

    def __init__(self, system_id, account, password):
        self.system_id = system_id
        self.account = account
        self.password = password
        self.token = '{"version":"v2.0.4","client":"ios","language":"en"}'
        self.global_url = 'https://globalapi.sems.com.cn/api/'
        self.base_url = self.global_url
        self.status = {-1: 'Offline', 1: 'Normal'}

    def getCurrentReadings(self):
        ''' Download the most recent readings from the GoodWe API. '''

        payload = {
            'powerStationId': self.system_id
        }

        # goodwe_server
        data = self.call("v1/PowerStation/GetMonitorDetailByPowerstationId", payload)

        inverterData = data['inverter'][0]

        result = {
            'status': self.status[inverterData['status']],
            'pgrid_w': inverterData['out_pac'],
            'eday_kwh': inverterData['eday'],
            'etotal_kwh': inverterData['etotal'],
            'grid_voltage': self.parseValue(inverterData['output_voltage'], 'V'),
            'latitude': data['info'].get('latitude'),
            'longitude': data['info'].get('longitude')
        }

        message = "{status}, {pgrid_w} W now, {eday_kwh} kWh today".format(**result)
        if result['status'] == 'Normal' or result['status'] == 'Offline':
            logging.info(message)
        else:
            logging.warning(message)

        return result



    def getRawPsOnlyBps(self):
        '''
        getRawPsOnlyBps is used to obtain the raw data from the Goodwe API endpoint without any modification
        to the returned message for endpoint: /v1/PowerStation/OnlyBps

        Goodwe documentation states the use for this endpoint as : "Whether the power station only has BPS"
        '''

        apiPayload = {
            'powerStationId': self.system_id
        }

        apiEndpoint = "/v1/PowerStation/OnlyBps"
        apiResponse = self.call(apiEndpoint, apiPayload)

        return apiResponse



    def getRawPsTime(self):
        '''
        getRawPsTime is used to obtain the raw data from the Goodwe API endpoint without any modification
        to the returned message for endpoint: /v1/PowerStation/GetPowerStaionTime. !!DO NOTE!! in V1 there is a typo in
        the API endpoint (GetPowerStaionTime) which is corrected in the Python function naming. When calling the endpoint
        manually you will have to take into account the typo in the endpoint.

        Goodwe documentation states the use for this endpoint as : "Get the current time of the power station"
        '''

        apiPayload = {
            'powerStationId': self.system_id
        }

        apiEndpoint = "/v1/PowerStation/GetPowerStaionTime"
        apiResponse = self.call(apiEndpoint, apiPayload)

        return apiResponse



    def getRawPsMonitorDetailByPowerstationId(self):
        ''' TODO document
        getRawPsMonitorDetailByPowerstationId is used to obtain the raw data from the Goodwe API endpoint without any
        modification to the returned message for endpoint: /v1/PowerStation/GetMonitorDetailByPowerstationId.

        Goodwe documentation states the use for this endpoint as : "Single power station homepage synthesis"
        '''

        apiPayload = {
            'powerStationId': self.system_id
        }

        apiEndpoint = "/v1/PowerStation/GetMonitorDetailByPowerstationId"
        apiResponse = self.call(apiEndpoint, apiPayload)

        return apiResponse


    def getRawPsPowerFlow(self):
        '''
        getRawPsPowerFlow is used to obtain the raw data from the Goodwe API endpoint without any
        modification to the returned message for endpoint: /v1/PowerStation/GetPowerFlow

        Goodwe documentation states the use for this endpoint as : "Obtain the energy flow diagram of a single power station"
        '''

        apiPayload = {
            'powerStationId': self.system_id
        }

        apiEndpoint = "/v1/PowerStation/GetPowerFlow"
        apiResponse = self.call(apiEndpoint, apiPayload)

        return apiResponse



    def getRawPsEnergyStatisticsCharts(self):
        '''
        TODO HAS A BUG WHICH NEED TO BE FIXED... IT REQUIRES MORE INPUT PARAMETERS
        Goodwe documentation states the use for this endpoint as : "Get energy trading chart"
        '''
        apiPayload = {
            'powerStationId': self.system_id,
            'date': 'xxx',
            'type': 'xxx',
            'opt': 'xxx'
        }

        apiEndpoint = "/v1/PowerStation/EnergeStatisticsCharts"
        apiResponse = self.call(apiEndpoint, apiPayload)

        return apiResponse



    def getRawPsSoc(self):
        '''
        getRawPsSoc is used to obtain the raw data from the Goodwe API endpoint without any
        modification to the returned message for endpoint: /v1/PowerStation/GetSoc

        Goodwe documentation states the use for this endpoint as : "Get the battery capacity of the power station"
        '''
        apiPayload = {
            'powerStationId': self.system_id
        }

        apiEndpoint = "/v1/PowerStation/GetSoc"
        apiResponse = self.call(apiEndpoint, apiPayload)

        return apiResponse



    def getRawPsPowerstationById(self):
        '''
        getRawPsPowerstationById is used to obtain the raw data from the Goodwe API endpoint without any
        modification to the returned message for endpoint: /v1/PowerStation/GetPowerStationById

        Goodwe documentation states the use for this endpoint as : "Get detailed information about the plant"
        '''

        apiPayload = {
            'powerStationId': self.system_id
        }

        apiEndpoint = "/v1/PowerStation/GetPowerStationById"
        apiResponse = self.call(apiEndpoint, apiPayload)

        return apiResponse



    def getRawPsInvertersByPowerStationId(self):
        '''
        getRawPsInvertersByPowerStationId is used to obtain the raw data from the Goodwe API endpoint without any
        modification to the returned message for endpoint: /v1/PowerStation/GetInvertersByPowerStationId

        Goodwe documentation states the use for this endpoint as : "Get plant equipment information"
        '''
        apiPayload = {
            'powerStationId': self.system_id
        }

        apiEndpoint = "/v1/PowerStation/GetInvertersByPowerStationId"
        apiResponse = self.call(apiEndpoint, apiPayload)

        return apiResponse



    def getRawPsInverterBySn(self, inverterSeriaNumber, inverterType):
        '''
        getRawPsInverterBySn is used to obtain the raw data from the Goodwe API endpoint without any
        modification to the returned message for endpoint: /v1/PowerStation/GetInverterBySn

        Goodwe documentation states the use for this endpoint as : "Get single device information"

        This call requires the following as a payload:
          {
           "inverterSn": "string",
           "type": "string"
          }
         Both the inverter Serial Number and the Inverter type need to be provided to getRawPsInverterKvBySn to be able
         make the call with the correct API payload. use getRawPsMonitorDetailByPowerstationId to get the required
         details. the response from getRawPsMonitorDetailByPowerstationId provides: inverter.*.sn for the serial number
         and inverter.*.type for the inverter type. In general only 1 inverter is returned so you can use the following:
            someVariable['inverter'][0]['sn']
            someVariable['inverter'][0]['type']
         providing the two above mentioned datapoints should enable you to retrieve the required information.
         '''

        apiPayload = {
            'inverterSn': inverterSeriaNumber,
            'type': inverterType
        }

        apiEndpoint = "/v1/PowerStation/GetInverterBySn"
        apiResponse = self.call(apiEndpoint, apiPayload)

        return apiResponse



    def getRawPsInverterKvBySn(self, inverterSeriaNumber, inverterType):
        '''
        getRawPsInverterKvBySn is used to obtain the raw data from the Goodwe API endpoint without any
        modification to the returned message for endpoint: /v1/PowerStation/GetInverterKvBySn

        Goodwe documentation states the use for this endpoint as : "Get device information, custom fields"

        This call requires the following as a payload:
         {
          "inverterSn": "string",
          "type": "string"
         }
        Both the inverter Serial Number and the Inverter type need to be provided to getRawPsInverterKvBySn to be able
        make the call with the correct API payload. use getRawPsMonitorDetailByPowerstationId to get the required
        details. the response from getRawPsMonitorDetailByPowerstationId provides: inverter.*.sn for the serial number
        and inverter.*.type for the inverter type. In general only 1 inverter is returned so you can use the following:
           someVariable['inverter'][0]['sn']
           someVariable['inverter'][0]['type']
        providing the two above mentioned datapoints should enable you to retrieve the required information.
        '''

        apiPayload = {
            'inverterSn': inverterSeriaNumber,
            'type': inverterType
        }

        apiEndpoint = "/v1/PowerStation/GetInverterKvBySn"
        apiResponse = self.call(apiEndpoint, apiPayload)

        return apiResponse



    def getRawPsKpiByPowerStationId(self):
        '''
        getRawPsKpiByPowerStationId is used to obtain the raw data from the Goodwe API endpoint without any
        modification to the returned message for endpoint: /v1/PowerStation/GetKpiByPowerStationId

        Goodwe documentation states the use for this endpoint as : "Get the KPI indicator of the power station"
        '''

        apiPayload = {
            'powerStationId': self.system_id
        }

        apiEndpoint = "/v1/PowerStation/GetKpiByPowerStationId"
        apiResponse = self.call(apiEndpoint, apiPayload)

        return apiResponse



    def getRawPsIsStoredInverter(self):
        '''
        getRawPsIsStoredInverter is used to obtain the raw data from the Goodwe API endpoint without any
        modification to the returned message for endpoint: /v1/PowerStation/IsStoredInverter

        Goodwe documentation states the use for this endpoint as : "Whether it is a solar storage device"
        '''

        apiPayload = {
            'powerStationId': self.system_id
        }

        apiEndpoint = "/v1/PowerStation/IsStoredInverter"
        apiResponse = self.call(apiEndpoint, apiPayload)

        return apiResponse



    def getRawPsIsStoredPowerStation(self):
        '''
        getRawPsIsStoredPowerStation is used to obtain the raw data from the Goodwe API endpoint without any
        modification to the returned message for endpoint: /v1/PowerStation/IsStoredPowerStation

        Goodwe documentation states the use for this endpoint as : "Whether it is a solar storage station"
         '''

        apiPayload = {
            'powerStationId': self.system_id
        }

        apiEndpoint = "/api/v1/PowerStation/IsStoredPowerStation"
        apiResponse = self.call(apiEndpoint, apiPayload)

        return apiResponse



    # POST /api/v1/PowerStation/UpdatePowerStationByPowerStationId
    # TODO check how to handle updates.



    def getRawPsPowerCharts(self, epoch, opt):
        '''
        getRawPsPowerCharts is used to obtain the raw data from the Goodwe API endpoint without any
        modification to the returned message for endpoint: /v1/PowerStation/GetPowerCharts

        Goodwe documentation states the use for this endpoint as : "Power station power curve chart"

        This call requires the following as a payload:

         {
          "powerStationId": "string",
          "date": "2019-01-24T11:08:49.893Z",
          "opt": "string"
         }

         The function takes the date as an epoch timestamp. Epoch is converted to an ISO 8601 (like)
         datetime format as required by the API endpoint.

        TODO find out the exact use of opt parameter in the apiPayLoad.
        '''

        payLoadDate = time.strftime('%Y-%m-%dT%H:%M.%SZ', time.localtime(float(epoch)))

        apiPayload = {
            'powerStationId': self.system_id,
            'date': payLoadDate,
            'opt': opt
        }

        apiEndpoint = "/api/v1/PowerStation/GetPowerCharts"
        apiResponse = self.call(apiEndpoint, apiPayload)

        return apiResponse



    def getRawPsExportPowerCharts(self):
        '''
         TODO add documentation POST /api/v1/PowerStation/ExportPowerCharts
         '''
        apiPayload = {
            'powerStationId': self.system_id
        }

        apiEndpoint = "/api/v1/PowerStation/ExportPowerCharts"
        apiResponse = self.call(apiEndpoint, apiPayload)

        return apiResponse


    def getRawPsYieldRatioCharts(self):
        '''
         TODO add documentation POST /api/v1/PowerStation/GetYieldRatioCharts
         '''
        apiPayload = {
            'powerStationId': self.system_id
        }

        apiEndpoint = "/api/v1/PowerStation/GetYieldRatioCharts"
        apiResponse = self.call(apiEndpoint, apiPayload)

        return apiResponse

    def getRawPsExportYieldRatioCharts(self):
        '''
         TODO add documentation POST /api/v1/PowerStation/ExportYieldRatioCharts
         '''
        apiPayload = {
            'powerStationId': self.system_id
        }

        apiEndpoint = "/api/v1/PowerStation/ExportYieldRatioCharts"
        apiResponse = self.call(apiEndpoint, apiPayload)

        return apiResponse

    def getRawPsInverterPowerChartsBySn(self):
        '''
         TODO add documentation POST /api/v1/PowerStation/GetInverterPowerChartsBySn
         '''
        apiPayload = {
            'powerStationId': self.system_id
        }

        apiEndpoint = "/api/v1/PowerStation/GetInverterPowerChartsBySn"
        apiResponse = self.call(apiEndpoint, apiPayload)

        return apiResponse



    def getRawPsExportInverterPowerChartsBySn(self):
        '''
         TODO add documentation POST /api/v1/PowerStation/ExportInverterPowerChartsBySn
         '''
        apiPayload = {
            'powerStationId': self.system_id
        }

        apiEndpoint = "/api/v1/PowerStation/ExportInverterPowerChartsBySn"
        apiResponse = self.call(apiEndpoint, apiPayload)

        return apiResponse


    def getRawPsInverterYieldRatioChartsBySn(self):
        '''
         TODO add documentation POST /api/v1/PowerStation/GetInverterYieldRatioChartsBySn
         '''
        apiPayload = {
            'powerStationId': self.system_id
        }

        apiEndpoint = "/api/v1/PowerStation/GetInverterYieldRatioChartsBySn"
        apiResponse = self.call(apiEndpoint, apiPayload)

        return apiResponse

    def getRawPsExportInverterYieldRatioChartsBySn(self):
        '''
         TODO add documentation POST /api/v1/PowerStation/ExportInverterYieldRatioChartsBySn
         '''
        apiPayload = {
            'powerStationId': self.system_id
        }

        apiEndpoint = "/api/v1/PowerStation/ExportInverterYieldRatioChartsBySn"
        apiResponse = self.call(apiEndpoint, apiPayload)

        return apiResponse


    def getRawPsExportPowerStaionPowerAndIncome(self):
        '''
         TODO add documentation POST /api/v1/PowerStation/ExportPowerStaionPowerAndIncome
         '''
        apiPayload = {
            'powerStationId': self.system_id
        }

        apiEndpoint = "/api/v1/PowerStation/ExportPowerStaionPowerAndIncome"
        apiResponse = self.call(apiEndpoint, apiPayload)

        return apiResponse


    def getRawPsExportInverterPowerAndIncome(self):
        '''
         TODO add documentation POST /api/v1/PowerStation/ExportInverterPowerAndIncome
         '''
        apiPayload = {
            'powerStationId': self.system_id
        }

        apiEndpoint = "/api/v1/PowerStation/ExportInverterPowerAndIncome"
        apiResponse = self.call(apiEndpoint, apiPayload)

        return apiResponse


    def getRawPsExportPowerstationPac(self):
        '''
         TODO add documentation POST /api/v1/PowerStation/ExportPowerstationPac
         '''
        apiPayload = {
            'powerStationId': self.system_id
        }

        apiEndpoint = "/api/v1/PowerStation/ExportPowerstationPac"
        apiResponse = self.call(apiEndpoint, apiPayload)

        return apiResponse


    def getDayReadings(self, date):
        date_s = date.strftime('%Y-%m-%d')

        payload = {
            'powerStationId': self.system_id
        }
        data = self.call("v1/PowerStation/GetMonitorDetailByPowerstationId", payload)
        if 'info' not in data:
            logging.warning(date_s + " - Received bad data " + str(data))
            return result

        result = {
            'latitude': data['info'].get('latitude'),
            'longitude': data['info'].get('longitude'),
            'entries': []
        }

        payload = {
            'powerstation_id': self.system_id,
            'count': 1,
            'date': date_s
        }
        data = self.call("PowerStationMonitor/GetPowerStationPowerAndIncomeByDay", payload)
        if len(data) == 0:
            logging.warning(date_s + " - Received bad data " + str(data))
            return result

        eday_kwh = data[0]['p']

        payload = {
            'id': self.system_id,
            'date': date_s
        }
        data = self.call("PowerStationMonitor/GetPowerStationPacByDayForApp", payload)
        if 'pacs' not in data:
            logging.warning(date_s + " - Received bad data " + str(data))
            return result

        minutes = 0
        eday_from_power = 0
        for sample in data['pacs']:
            parsed_date = datetime.strptime(sample['date'], "%m/%d/%Y %H:%M:%S")
            next_minutes = parsed_date.hour * 60 + parsed_date.minute
            sample['minutes'] = next_minutes - minutes
            minutes = next_minutes
            eday_from_power += sample['pac'] * sample['minutes']
            factor = eday_kwh / eday_from_power if eday_from_power > 0 else 1

            eday_kwh = 0
        for sample in data['pacs']:
            date += timedelta(minutes=sample['minutes'])
            pgrid_w = sample['pac']
            increase = pgrid_w * sample['minutes'] * factor
            if increase > 0:
                eday_kwh += increase
                result['entries'].append({
                    'dt': date,
                    'pgrid_w': pgrid_w,
                    'eday_kwh': round(eday_kwh, 3)
                })

        return result

    def call(self, url, payload):
        for i in range(1, 4):
            try:
                headers = {'User-Agent': 'PVMaster/2.0.4 (iPhone; iOS 11.4.1; Scale/2.00)', 'Token': self.token}

                r = requests.post(self.base_url + url, headers=headers, data=payload, timeout=10)
                r.raise_for_status()
                data = r.json()
                logging.debug(data)

                if data['msg'] == 'success' and data['data'] is not None:
                    return data['data']
                else:
                    loginPayload = {'account': self.account, 'pwd': self.password}
                    r = requests.post(self.global_url + 'v1/Common/CrossLogin', headers=headers, data=loginPayload,
                                          timeout=10)
                    r.raise_for_status()
                    data = r.json()
                    self.base_url = data['api']
                    self.token = json.dumps(data['data'])
            except requests.exceptions.RequestException as exp:
                logging.warning(exp)
            time.sleep(i ** 3)
        else:
            logging.error("Failed to call GoodWe API")

        return {}

    def parseValue(self, value, unit):
        try:
            return float(value.rstrip(unit))
        except ValueError as exp:
            logging.warning(exp)
            return 0
