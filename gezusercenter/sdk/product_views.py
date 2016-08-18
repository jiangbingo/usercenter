# -*- encoding: utf-8 -*-
import base64
import hashlib
import os
import ConfigParser
from zipfile import ZipFile
from rest_framework import viewsets
from django.core.files.base import ContentFile
from products.product_utils import *
from rest_framework import status
from rest_framework.decorators import list_route
from rest_framework.response import Response
from django.db.models import Q
from pre_check import PermissionCheck
from usermanager.models import AccountKey
from products.models import (Product, ProductAttribute, ProductModelPreviews,
                             ProductModelFiles, ProductDistributor, ProductModel, ProductModelZip)
from django.core.cache import cache
from toolkit.utils import get_models_path, get_models_base_path
from toolkit.xmltodict import parse
from toolkit.convert_obj_three import createjs
from toolkit.mylogger import Logger

class ProductViewSet(PermissionCheck, viewsets.ViewSet):
    """
        产品管理
    """
    max_size = 3 * 10124 * 1024

    def create(self, request):
        """
        :param request:
        :return:
        """
        return Response(json.dumps({}), status.HTTP_200_OK)

    def list(self, request):
        """
        :param request:
        :return:
        """
        return Response(json.dumps({}), status.HTTP_200_OK)

    @list_route(methods=['get', 'post'])
    def add(self, request):
        """
        :param request:
        :return:
        """
        Logger.debug("get cmd: add product!")
        request_data = self._get_request_data(request)
        try:
            app_secret = request.META.get("HTTP_SECDATA", "")
            data = json.loads(request_data.get("data", ""))
            if data == "":
                return self._return({"code": 1, "msg": "add product failed.", "content": ""})
            pd = Product(name=data.get("name"), color=data.get("color"), material=data.get("material"),
                         norms_no=data.get("norms_no"), remark=data.get("remark"), technics=data.get("technics"),
                         category_id=data.get("c3"), brand_id=data.get("brand"), manufactor_id=data.get("manufactor"),
                         series_id=data.get("series"), args=json.dumps(data.get("args")), create_time=int(time.time()),
                         price=data.get("price", 0), lay_status=data.get("lay_status"),
                         is_platform=data.get("is_platform", False), is_hardness=data.get("is_hardness", False),
                         furn_set=data.get("furn_set"), other_model_args=json.dumps(data.get("other_model_args", {})))
            size = data.get("size", "")
            if len(size) == 3:
                pd.length = size[0]
                pd.width = size[1]
                pd.height = size[2]
            pd.save()
            key = AccountKey.objects.select_related("account").filter(app_secret=app_secret).first()
            if key:
                account = key.account
                if hasattr(account, "distributors"):
                    dist = account.distributors
                    ProductDistributor(product=pd, distributor=dist).save()
            pd.generate_product_no()
            attrs = data.get("attrs", {})
            if attrs:
                for key, value in attrs.items():
                    ProductAttribute(product=pd, attribute_id=key, value=value).save()
            img = data.get("img", None)
            if isinstance(img, dict) and img.get("name"):
                file_name = pd.product_no + img.get("name", "")
                ptmodel = ProductModelPreviews(product=pd, name=file_name)
                ptmodel.file.save(file_name, ContentFile(base64.b64decode(img.get("content", ""))))
                ptmodel.save()
            return self._return({"code": 0, "msg": "add product success.", "content": {"product_no": pd.product_no}})
        except Exception as e:
            Logger.error("add product error: {}".format(e))
            return self._return({"code": 1, "msg": e.message, "content": ""})

    @list_route(methods=['get', 'post'])
    def addmodel(self, request):
        """
        :param request:
        :return:
        """
        Logger.debug("get cmd: add product model!")
        request_data = self._get_request_data(request)
        product_no = request_data.get("product_no")
        model = request_data.get("model", "")
        if product_no is None or model == "":
            return self._return({"code": 1, "msg": "param is null.", "content": ""})
        product = Product.objects.filter(product_no=product_no).first()
        if not product:
            return self._return({"code": 2, "msg": "product_no is invalid.", "content": ""})
        model = json.loads(model)
        name = str(model.get("name", ""))
        if name == "":
            return self._return({"code": 3, "msg": "", "content": ""})
        name = "{0}_{1}.{2}".format(product_no, name, model.get("type", ""))
        content = base64.b64decode(model.get("file", ""))
        length = model.get("size")
        # if length > self.max_size and length != len(content):
        #     return self._return({"code": 4, "msg": "size too big!", "content": ""})
        code = model.get("code")
        md = hashlib.md5()
        md.update(content)
        if code != md.hexdigest():
            return self._return({"code": 5, "msg": "file code check failed!", "content": ""})
        times = int(model.get("times"))
        which = int(model.get("which"))
        if times < 1 or which < 1 or which > times:
            return self._return({"code": 6, "msg": "times, which error!", "content": ""})
        if times == 1:
            pmodel = ProductModelZip(product=product)
            pmodel.file.save(name, ContentFile(content))
            pmodel.save()
            try:
                response = self._save_model_file(product, get_models_base_path(), name)
                return self._return(response)
            except Exception, e:
                Logger.error("addmodel get error: {}".format(e))
                return self._return({"code": 7, "msg": "save file error: {}".format(e), "content": ""})
        else:
            if which == 1 and os.path.exists(name):
                os.remove(name)
                cache.delete(name)
            point = cache.get(name, 0)
            if which == times:
                cache.delete(name)
            else:
                cache.set(name, which)
            if point + 1 == which:
                path = get_models_base_path()
                if not os.path.exists(path):
                    os.makedirs(path)
                with open(os.path.join(path, name), "ab") as fd:
                    fd.write(content)
                if which == times:
                    pmodel = ProductModelZip(product=product)
                    pmodel.file.name = os.path.join(get_models_path(), name)
                    pmodel.save()
                    try:
                        response_data = self._save_model_file(product, path, name)
                        return self._return(response_data)
                    except Exception, e:
                        Logger.error("addmodel get error: {}".format(e))
                        return self._return({"code": 7, "msg": "save file error: {}".format(e), "content": ""})
                return self._return({"code": 0, "msg": "file upload successful!", "content": ""})
            else:
                return self._return({"code": 5, "msg": "which field is invalid!", "content": ""})

    @list_route(methods=['get', 'post'])
    def update(self, request):
        """
        :param request:
        :return:
        """
        Logger.debug("get cmd update product!")
        product_data = self._get_request_data(request)
        product_no = product_data.get("product_no")
        fields = product_data.get("fields", {})
        if product_data is None or fields == {}:
            return self._return({"code": 1, "msg": "param error!", "content": ""})
        fields = json.loads(fields)
        product = Product.objects.prefetch_related("attributes", "previews").filter(product_no=product_no).first()
        if product:
            for key, value in fields.items():
                if key == "name":
                    product.name = value
                elif key == "size":
                    if len(value) == 3:
                        product.length = value[0]
                        product.width = value[1]
                        product.height = value[2]
                elif key == "color":
                    product.color = value
                elif key == "material":
                    product.material = value
                elif key == "args":
                    product.args = json.dumps(value)
                elif key == "norms_no":
                    product.norms_no = value
                elif key == "remark":
                    product.remark = value
                elif key == "technics":
                    product.technics = value
                elif key == "attrs":
                    if hasattr(product, "attributes") and isinstance(value, dict):
                        for ky, val in value.items():
                            attr = product.attributes.filter(attribute_id=ky).first()
                            if attr:
                                attr.value = val
                                attr.save()
                            else:
                                ProductAttribute(product=product, attribute_id=ky, value=value).save()
                elif key == "brand":
                    product.brand_id = value
                elif key == "series":
                    product.series_id = value
                elif key == "manufactor":
                    product.manufactor_id = value
                elif key == "img":
                    if isinstance(value, dict):
                        file_name = product.product_no + value.get("name", "")
                        pdmodel = product.previews.all().first()
                        if pdmodel:
                            pdmodel.file.save(file_name, ContentFile(base64.b64decode(value.get("content", ""))))
                            pdmodel.save()
                        else:
                            pdmodel = ProductModelPreviews(product=product, name=file_name)
                            pdmodel.file.save(file_name, ContentFile(base64.b64decode(value.get("content", ""))))
                            pdmodel.save()
            try:
                product.update_time = int(time.time())
                product.save()
            except Exception, e:
                return self._return({"code": 2, "msg": e, "content": ""})
        else:
            return self._return({"code": 2, "msg": "product is not exists!", "content": ""})
        return self._return({"code": 0, "msg": "update successful!", "content": ""})

    @list_route(methods=['get', 'post'])
    def query(self, request):
        """
        :param request:
        :return:
        """
        Logger.debug("get cmd query product!")
        request_data = self._get_request_data(request)
        product_nos = request_data.get("product_nos", [])
        if product_nos is None:
                return self._return({"code": 1, "msg": "product_nos is null.", "content": ""})
        result = {}
        for product_no in product_nos:
            product = Product.object.filter(Q(product_no=product_no) & Q(active=1)).first()
            if product:
                message = {
                    "name": product.name,
                    "c1": product.category.id,
                    "c2": product.category.parent_category.id,
                    "c3": product.category.parent_category.parent_category.id,
                    "brand": product.brand_id,
                    "series": product.series_id,
                    "manufactor": product.manufactor_id,
                    "size": [product.length, product.width, product.height],
                    "color": product.color,
                    "material": product.material,
                    "norms_no": product.norms_no,
                    "remark": product.remark,
                    "technics": product.technics,
                    "models": [],
                    "img": "",
                    "attrs": ""}
                result[str(product.product_no)] = message
        return self._return({"code": 0, "msg": "query data successful.", "content": result})

    @list_route(methods=['get', 'post'])
    def delete(self, request):
        """
        :param request:
        :return:
        """
        Logger.debug("get cmd delete product!")
        request_data = self._get_request_data(request)
        product_nos = {}
        # import ipdb;ipdb.set_trace()
        try:
            product_nos = json.loads(request_data.get("product_nos"))
        except Exception, e:
            Logger.error("json decode product_nos error:{}".format(e))
            return self._return({"code": 1, "msg": "product_nos is invalid.", "content": ""})
        if (not isinstance(product_nos, list)) or len(product_nos) == 0:
                return self._return({"code": 1, "msg": "product_nos is null.", "content": ""})
        nos = []
        code = 0
        msg = "delete products successful!"
        for product_no in product_nos:
            product = Product.objects.filter(product_no=product_no).first()
            if product:
                try:
                    product.status = False
                    product.save()
                    nos.append(product_no)
                except Exception, e:
                    code = 2
                    msg = "delete products failed!"
                    Logger.error("delete product failed :{}".format(e))
            else:
                code = 3
                msg = "product_no is invalid!"
        return self._return({"code": code, "msg": msg, "content": {"product_nos": nos}})

    @staticmethod
    def _get_request_data(request):
        if request.method == "GET":
            return request.GET
        else:
            return request.POST

    @staticmethod
    def _save_model_file(product, path, name):
        extrac_path = os.path.join(path, name.split(".")[0])
        zf = ZipFile(os.path.join(path, name), "r")
        zf.extractall(extrac_path.split(".")[0])
        zf.close()
        config_path = os.path.join(extrac_path, "map.txt")
        if not os.path.exists(config_path):
            return {"code": 7, "msg": "config.xml is not exists.", "content": ""}
        f_path = os.path.join(get_models_path(), name.split(".")[0])
        config_parse = ConfigParser.ConfigParser()
        config_parse.read(os.path.join(extrac_path, "map.txt"))
        name = None
        if config_parse.has_option("modelname", "name"):
            name = config_parse.get("modelname", "name").decode("gbk").encode("utf-8")
        if config_parse.has_option("chanpintupian", "tupian"):
            photos = config_parse.get("chanpintupian", "tupian")
            try:
                photos = photos.split(",")
                if isinstance(photos, list) and len(photos) > 0:
                    pmodel = ProductModel(product=product, name=name, source="chanpintupian")
                    pmodel.save()
                    for photo in photos:
                        if photo != "":
                            ProductModelFiles(model=pmodel, file=os.path.join(f_path, photo), type="tupian").save()
            except Exception, e:
                Logger.error("upload product model error, decode chanpintupian error: {}".format(e))
        if config_parse.has_option("kongjiandashi2D", "tupian"):
            photos = config_parse.get("kongjiandashi2D", "tupian")
            try:
                photos = photos.split(",")
                if isinstance(photos, list) and len(photos) > 0:
                    pmodel = ProductModel(product=product, name=name, source="kongjiandashi2D")
                    pmodel.save()
                    for photo in photos:
                        if photo != "":
                            ProductModelFiles(model=pmodel, file=os.path.join(f_path, photo), type="tupian").save()
            except Exception, e:
                Logger.error("upload product model error, decode chanpintupian error: {}".format(e))
        if config_parse.has_section("kongjiandashi3D") and len(config_parse.options("kongjiandashi3D")) > 0:
            pmodel = ProductModel(product=product, name=name, source="kongjiandashi3D")
            pmodel.save()
            if config_parse.has_option("kongjiandashi3D", "moxing_obj"):
                moxing_obj = config_parse.get("kongjiandashi3D", "moxing_obj")
                if len(moxing_obj) > 0:
                    # old_bins = ProductModelFiles.objects.filter(type="bin")
                    # if old_bins.exists():
                    #     for old_bin in old_bins:
                    #         old_bin.active = False
                    #         old_bin.save()
                    # old_js = ProductModelFiles.objects.filter(type="js")
                    # if old_js.exists():
                    #     for js in old_js:
                    #         js.active = False
                    #         js.save()
                    ProductModelFiles(model=pmodel, file=os.path.join(f_path, moxing_obj), type="moxing_obj").save()
            if config_parse.has_option("kongjiandashi3D", "moxing_mtl"):
                moxing_mtl = config_parse.get("kongjiandashi3D", "moxing_mtl")
                if len(moxing_mtl) > 0:
                    ProductModelFiles(model=pmodel, file=os.path.join(f_path, moxing_mtl), type="moxing_mtl").save()
            if config_parse.has_option("kongjiandashi3D", "faxiantu"):
                faxiantu = config_parse.get("kongjiandashi3D", "faxiantu")
                if len(faxiantu) > 0:
                    ProductModelFiles(model=pmodel, file=os.path.join(f_path, faxiantu), type="faxiantu").save()
            if config_parse.has_option("kongjiandashi3D", "tietu"):
                tietu = config_parse.get("kongjiandashi3D", "tietu")
                if len(tietu) > 0:
                    ProductModelFiles(model=pmodel, file=os.path.join(f_path, tietu), type="tietu").save()
            if config_parse.has_option("kongjiandashi3D", "yinying"):
                yinying = config_parse.get("kongjiandashi3D", "yinying")
                if len(yinying) > 0:
                    ProductModelFiles(model=pmodel, file=os.path.join(f_path, yinying), type="yinying").save()
        if config_parse.has_option("xuanran3D", "3dmax"):
            tdmax = config_parse.get("xuanran3D", "3dmax")
            if len(tdmax) > 0:
                ProductModelFiles(model=pmodel, file=os.path.join(f_path, tdmax), type="3dmax").save()
        if config_parse.has_option("peishizushou", "tupian"):
            photos = config_parse.get("peishizushou", "tupian")
            try:
                photos = photos.split(",")
                if isinstance(photos, list) and len(photos) > 0:
                    pmodel = ProductModel(product=product, name=name, source="peishizushou")
                    pmodel.save()
                    for photo in photos:
                        if photo != "":
                            ProductModelFiles(model=pmodel, file=os.path.join(f_path, photo), type="tupian").save()
            except Exception, e:
                Logger.error("upload product model error, decode chanpintupian error: {}".format(e))
        if config_parse.has_section("IOS"):
            pass
        if config_parse.has_section("Android"):
            pass
        if config_parse.has_section("PC"):
            pass
        return {"code": 0, "msg": "file upload successful!", "content": ""}

    @staticmethod
    def _return(data):
        Logger.info("return data is: {}".format(data))
        return Response(json.dumps(data), status.HTTP_200_OK)

    # @staticmethod
    # def _save_model_file(product, path, name):
    #     time_str = str(time.time()).replace(".", "")
    #     extrac_path = os.path.join(path, time_str)
    #     zf = ZipFile(os.path.join(path, name), "r")
    #     zf.extractall(extrac_path)
    #     zf.close()
    #     config_path = os.path.join(extrac_path, "map.xml")
    #     if not os.path.exists(config_path):
    #         return {"code": 7, "msg": "config.xml is not exists.", "content": ""}
    #     with open(config_path, "r") as fd:
    #         maps = fd.read()
    #     f_path = os.path.join(get_models_path(), time_str)
    #     maps = parse(maps)["config"]
    #     name = maps.get("name")
    #     scenes = maps.get("scenes")
    #     c_photo = scenes.get("chanpintupian")
    #     if c_photo:
    #         pmodel = ProductModel(product=product, name=name, source="chanpintupian")
    #         pmodel.save()
    #         photos = c_photo.get("tupian").get("img")
    #         if not isinstance(photos, list):
    #             photos = [photos]
    #         for photo in photos:
    #             if photo is not None:
    #                 ProductModelFiles(model=pmodel, file=os.path.join(f_path, photo), type="tupian").save()
    #     space_2d = scenes.get("kongjiandashi2D")
    #     if space_2d:
    #         pmodel = ProductModel(product=product, name=name, source="kongjiandashi2D")
    #         pmodel.save()
    #         photos = space_2d.get("tupian").get("img")
    #         if not isinstance(photos, list):
    #             photos = [photos]
    #         for photo in photos:
    #             if photo is not None:
    #                 ProductModelFiles(model=pmodel, file=os.path.join(f_path, photo), type="tupian").save()
    #     space_3d = scenes.get("kongjiandashi3D")
    #     if space_3d:
    #         pmodel = ProductModel(product=product, name=name, source="kongjiandashi3D")
    #         pmodel.save()
    #         moxing_obj = space_3d.get("moxing_obj")
    #         if moxing_obj is not None:
    #             ProductModelFiles(model=pmodel, file=os.path.join(f_path, moxing_obj), type="moxing_obj").save()
    #         moxing_mtl = space_3d.get("moxing_mtl")
    #         if moxing_mtl is not None:
    #             ProductModelFiles(model=pmodel, file=os.path.join(f_path, moxing_mtl), type="moxing_mtl").save()
    #         faxiantu = space_3d.get("faxiantu")
    #         if faxiantu is not None:
    #             ProductModelFiles(model=pmodel, file=os.path.join(f_path, faxiantu), type="faxiantu").save()
    #         tietu = space_3d.get("tietu")
    #         if tietu is not None:
    #             ProductModelFiles(model=pmodel, file=os.path.join(f_path, tietu), type="tietu").save()
    #         yinying = space_3d.get("yinying")
    #         if yinying is not None:
    #             ProductModelFiles(model=pmodel, file=os.path.join(f_path, yinying), type="yinying").save()
    #     color_3d = scenes.get("xuanran3D")
    #     if color_3d:
    #         tdmax = color_3d.get("tdmax")
    #         if tdmax is not None:
    #             ProductModelFiles(model=pmodel, file=os.path.join(f_path, tdmax), type="3dmax").save()
    #     ios = scenes.get("IOS")
    #     if ios:
    #         pass
    #     android = scenes.get("android")
    #     if android:
    #         pass
    #     return {"code": 0, "msg": "file upload successful!", "content": ""}