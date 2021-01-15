# import redis
# from django.conf import settings
# from .models import Product


# # connect to redis
# r = redis.Redis(host=settings.REDIS_HOST,
#                 port=settings.REDIS_PORT,
#                 db=settings.REDIS_DB)


# class Recommender(object):

#     def get_product_key(self, id):
#         return f'product:{id}:purchased_with'

#     def the_ids_bought(self, the_ids): # this parameter can be nmed anything
#         product_ids = [p.id for p in the_ids]
#         for product_id in product_ids:
#             for other_product_id in product_ids:
#                 # get the other the_ids bought with each product
#                 if product_id != other_product_id:
#                     # increment score for product purchased together
#                     r.zincrby(self.get_product_key(product_id), 1, other_product_id)

#     def suggest_products_for(self, the_ids, max_results=6):
#         product_ids = [p.id for p in the_ids]
#         if len(the_ids) == 1:
#             # only 1 product
#             suggestions = r.zrange(self.get_product_key(product_ids[0]), 0, -1, desc=True)[:max_results]
#         else:
#             # generate a temporary key
#             tmp_key = f'tmp_{[str(id) for id in product_ids]}'
#             # multiple the_ids, combine scores of all the_ids
#             # store the resulting sorted set in a temporary key
#             keys = [self.get_product_key(id) for id in product_ids]
#             r.zunionstore(tmp_key, keys)
#             # remove ids for the products the recommendation is for
#             r.zrem(tmp_key, *product_ids)
#             # get the product ids by their score, descendant sort
#             suggestions = r.zrange(tmp_key, 0, -1,
#                                    desc=True)[:max_results]
#             # remove the temporary key
#             r.delete(tmp_key)
#         suggested_products_ids = [int(id) for id in suggestions]

#         # get suggested the_ids and sort by order of appearance
#         suggested_the_ids = list(Product.objects.filter(id__in=suggested_products_ids))
#         suggested_the_ids.sort(key=lambda x: suggested_products_ids.index(x.id))
#         return suggested_the_ids

#     def clear_purchases(self):
#         for id in Product.objects.values_list('id', flat=True):
#             r.delete(self.get_product_key(id))
