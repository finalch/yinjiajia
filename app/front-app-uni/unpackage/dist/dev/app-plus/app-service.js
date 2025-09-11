if (typeof Promise !== "undefined" && !Promise.prototype.finally) {
  Promise.prototype.finally = function(callback) {
    const promise = this.constructor;
    return this.then(
      (value) => promise.resolve(callback()).then(() => value),
      (reason) => promise.resolve(callback()).then(() => {
        throw reason;
      })
    );
  };
}
;
if (typeof uni !== "undefined" && uni && uni.requireGlobal) {
  const global = uni.requireGlobal();
  ArrayBuffer = global.ArrayBuffer;
  Int8Array = global.Int8Array;
  Uint8Array = global.Uint8Array;
  Uint8ClampedArray = global.Uint8ClampedArray;
  Int16Array = global.Int16Array;
  Uint16Array = global.Uint16Array;
  Int32Array = global.Int32Array;
  Uint32Array = global.Uint32Array;
  Float32Array = global.Float32Array;
  Float64Array = global.Float64Array;
  BigInt64Array = global.BigInt64Array;
  BigUint64Array = global.BigUint64Array;
}
;
if (uni.restoreGlobal) {
  uni.restoreGlobal(Vue, weex, plus, setTimeout, clearTimeout, setInterval, clearInterval);
}
(function(vue) {
  "use strict";
  function formatAppLog(type, filename, ...args) {
    if (uni.__log__) {
      uni.__log__(type, filename, ...args);
    } else {
      console[type].apply(console, [...args, filename]);
    }
  }
  const APP_PREFIX = "APP";
  const USER_KEY = `${APP_PREFIX}_USER`;
  function tokenKey(uid) {
    return `${APP_PREFIX}_TOKEN:${uid || "ANON"}`;
  }
  function tokenExpKey(uid) {
    return `${APP_PREFIX}_TOKEN_EXPIRES_AT:${uid || "ANON"}`;
  }
  function safeSetStorage(key, value) {
    try {
      uni.setStorageSync(key, value);
    } catch (e) {
      formatAppLog("warn", "at src/utils/auth.js:17", "设置存储失败:", e);
    }
  }
  function safeGetStorage(key, defaultValue = "") {
    try {
      return uni.getStorageSync(key) || defaultValue;
    } catch (e) {
      formatAppLog("warn", "at src/utils/auth.js:25", "获取存储失败:", e);
      return defaultValue;
    }
  }
  function safeRemoveStorage(key) {
    try {
      uni.removeStorageSync(key);
    } catch (e) {
      formatAppLog("warn", "at src/utils/auth.js:34", "删除存储失败:", e);
    }
  }
  function setToken(token, expiresAt) {
    const uid = getUserId() || "ANON";
    safeSetStorage(tokenKey(uid), token);
    if (expiresAt)
      safeSetStorage(tokenExpKey(uid), expiresAt);
  }
  function getToken() {
    const uid = getUserId() || "ANON";
    return safeGetStorage(tokenKey(uid), "");
  }
  function clearToken() {
    const uid = getUserId() || "ANON";
    safeRemoveStorage(tokenKey(uid));
    safeRemoveStorage(tokenExpKey(uid));
  }
  function setUser(user) {
    safeSetStorage(USER_KEY, JSON.stringify(user || {}));
  }
  function getUser() {
    try {
      const userStr = safeGetStorage(USER_KEY, "{}");
      return JSON.parse(userStr);
    } catch (e) {
      formatAppLog("warn", "at src/utils/auth.js:64", "解析用户信息失败:", e);
      return {};
    }
  }
  function getUserId() {
    const u = getUser();
    return u && u.user_id ? u.user_id : null;
  }
  function clearUser() {
    safeRemoveStorage(USER_KEY);
  }
  const config = {
    // 开发环境
    development: {
      baseURL: "http://192.168.1.15:6000",
      timeout: 1e4
    },
    // 生产环境
    production: {
      baseURL: "https://your-production-domain.com",
      timeout: 1e4
    },
    // 测试环境
    test: {
      baseURL: "https://your-test-domain.com",
      timeout: 1e4
    }
  };
  function getCurrentEnv() {
    return "development";
  }
  const apiConfig = config[getCurrentEnv()] || config.development;
  const baseURL = apiConfig.baseURL;
  const timeout = apiConfig.timeout;
  const interceptors = {
    request: [],
    response: []
  };
  function addRequestInterceptor(onFulfilled, onRejected) {
    interceptors.request.push({
      onFulfilled,
      onRejected
    });
  }
  function addResponseInterceptor(onFulfilled, onRejected) {
    interceptors.response.push({
      onFulfilled,
      onRejected
    });
  }
  function executeRequestInterceptors(config2) {
    let result = config2;
    for (const interceptor of interceptors.request) {
      try {
        if (interceptor.onFulfilled) {
          result = interceptor.onFulfilled(result) || result;
        }
      } catch (error) {
        if (interceptor.onRejected) {
          interceptor.onRejected(error);
        }
      }
    }
    return result;
  }
  function executeResponseInterceptors(response) {
    let result = response;
    for (const interceptor of interceptors.response) {
      try {
        if (interceptor.onFulfilled) {
          result = interceptor.onFulfilled(result) || result;
        }
      } catch (error) {
        if (interceptor.onRejected) {
          interceptor.onRejected(error);
        }
      }
    }
    return result;
  }
  const request = (options) => {
    return new Promise((resolve, reject) => {
      var _a;
      const token = getToken();
      let config2 = {
        url: baseURL + options.url,
        method: options.method || "GET",
        data: options.data || {},
        header: {
          "Content-Type": "application/json",
          ...options.header
        },
        timeout,
        success: (res) => {
          formatAppLog("log", "at src/utils/request.js:85", "Response:", res.statusCode, res.data);
          const processedResponse = executeResponseInterceptors({
            data: res.data,
            status: res.statusCode,
            headers: res.header,
            config: options
          });
          resolve(processedResponse);
        },
        fail: (err) => {
          formatAppLog("error", "at src/utils/request.js:98", "Request Error:", err);
          const processedError = executeResponseInterceptors({
            error: err,
            config: options
          });
          reject(processedError);
        }
      };
      formatAppLog("log", "at src/utils/request.js:111", "-----token:", token);
      if (token) {
        config2.header["Authorization"] = `Bearer ${token}`;
      }
      config2 = executeRequestInterceptors(config2);
      formatAppLog("log", "at src/utils/request.js:119", "Request:", (_a = config2.method) == null ? void 0 : _a.toUpperCase(), config2);
      uni.request(config2);
    });
  };
  const get = (url, params = {}, config2 = {}) => {
    let queryString = "";
    if (Object.keys(params).length > 0) {
      queryString = "?" + Object.keys(params).map((key) => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`).join("&");
    }
    return request({
      url: url + queryString,
      method: "GET",
      ...config2
    });
  };
  const post = (url, data = {}, config2 = {}) => {
    return request({
      url,
      method: "POST",
      data,
      ...config2
    });
  };
  const put = (url, data = {}, config2 = {}) => {
    return request({
      url,
      method: "PUT",
      data,
      ...config2
    });
  };
  const del = (url, config2 = {}) => {
    return request({
      url,
      method: "DELETE",
      ...config2
    });
  };
  addRequestInterceptor((config2) => {
    const token = getToken();
    if (token) {
      config2.header = config2.header || {};
      config2.header["Authorization"] = `Bearer ${token}`;
    }
    return config2;
  });
  addResponseInterceptor((response) => {
    if (response.data && response.data.code === 401) {
      clearToken();
      clearUser();
      uni.showToast({
        title: "登录已过期，请重新登录",
        icon: "none",
        duration: 2e3
      });
      setTimeout(() => {
        uni.reLaunch({
          url: "/pages/login/login"
        });
      }, 2e3);
      return Promise.reject(new Error("登录已过期"));
    }
    if (response.data && response.data.code !== 200) {
      uni.showToast({
        title: response.data.message || "请求失败",
        icon: "none"
      });
    }
    return response;
  });
  const request$1 = {
    request,
    get,
    post,
    put,
    delete: del,
    addRequestInterceptor,
    addResponseInterceptor
  };
  const productApi = {
    // 获取商品列表
    getProducts(params = {}) {
      return request$1.get("/api/app/product/", params);
    },
    // 获取商品详情
    getProductDetail(productId) {
      return request$1.get(`/api/app/product/${productId}`);
    },
    // 获取商品分组
    getGroups() {
      return request$1.get("/api/app/product/groups");
    }
  };
  const cartApi = {
    // 获取购物车列表
    getCart(userId = 1) {
      return request$1.get("/api/app/cart/", {
        user_id: userId
      });
    },
    // 添加商品到购物车
    addToCart(data) {
      return request$1.post("/api/app/cart/", data);
    },
    // 快捷加入购物车（商品页默认选择第一个规格）
    quickAddToCart({
      productId,
      userId = 1,
      quantity = 1,
      specCombinationId
    }) {
      const payload = {
        user_id: userId,
        product_id: productId,
        quantity
      };
      if (specCombinationId)
        payload.spec_combination_id = specCombinationId;
      return request$1.post("/api/app/cart/", payload);
    },
    // 更新购物车商品数量
    updateCartItem(itemId, data) {
      return request$1.put(`/api/app/cart/${itemId}`, data);
    },
    // 删除购物车商品
    removeCartItem(itemId, userId = 1) {
      return request$1.delete(`/api/app/cart/${itemId}?user_id=${userId}`);
    },
    // 清空购物车
    clearCart(userId = 1) {
      return request$1.delete(`/api/app/cart/clear?user_id=${userId}`);
    }
  };
  const authApi = {
    register({
      phone,
      password
    }) {
      return request$1.post("/api/app/auth/register", {
        phone,
        password
      });
    },
    login({
      phone,
      password
    }) {
      return request$1.post("/api/app/auth/login", {
        phone,
        password
      });
    },
    validate(token) {
      return request$1.get("/api/app/auth/validate", {
        token
      });
    }
  };
  class CategoryService {
    constructor() {
      this.baseUrl = "/api/g/category/";
    }
    // 获取品类列表
    async getCategories(params = {}) {
      var _a;
      try {
        const response = await request$1.get(this.baseUrl, params);
        if (response.data.code === 200) {
          return {
            success: true,
            data: response.data.data.list || [],
            total: ((_a = response.data.data.list) == null ? void 0 : _a.length) || 0
          };
        } else {
          return {
            success: false,
            message: response.data.message || "获取品类列表失败",
            data: []
          };
        }
      } catch (error) {
        formatAppLog("error", "at src/services/categoryService.js:27", "获取品类列表失败:", error);
        return {
          success: false,
          message: "网络错误，请重试",
          data: []
        };
      }
    }
    // 获取单个品类详情
    async getCategory(categoryId) {
      try {
        const response = await request$1.get(`${this.baseUrl}/${categoryId}`);
        if (response.data.code === 200) {
          return {
            success: true,
            data: response.data.data
          };
        } else {
          return {
            success: false,
            message: response.data.message || "获取品类详情失败"
          };
        }
      } catch (error) {
        formatAppLog("error", "at src/services/categoryService.js:53", "获取品类详情失败:", error);
        return {
          success: false,
          message: "网络错误，请重试"
        };
      }
    }
    // 创建品类（如果需要的话）
    async createCategory(categoryData) {
      try {
        const response = await request$1.post(this.baseUrl, categoryData);
        if (response.data.code === 200) {
          return {
            success: true,
            data: response.data.data,
            message: "创建品类成功"
          };
        } else {
          return {
            success: false,
            message: response.data.message || "创建品类失败"
          };
        }
      } catch (error) {
        formatAppLog("error", "at src/services/categoryService.js:79", "创建品类失败:", error);
        return {
          success: false,
          message: "网络错误，请重试"
        };
      }
    }
    // 更新品类（如果需要的话）
    async updateCategory(categoryId, categoryData) {
      try {
        const response = await request$1.put(`${this.baseUrl}/${categoryId}`);
        if (response.data.code === 200) {
          return {
            success: true,
            data: response.data.data,
            message: "更新品类成功"
          };
        } else {
          return {
            success: false,
            message: response.data.message || "更新品类失败"
          };
        }
      } catch (error) {
        formatAppLog("error", "at src/services/categoryService.js:105", "更新品类失败:", error);
        return {
          success: false,
          message: "网络错误，请重试"
        };
      }
    }
    // 删除品类（如果需要的话）
    async deleteCategory(categoryId) {
      try {
        const response = await request$1.delete(`${this.baseUrl}/${categoryId}`);
        if (response.data.code === 200) {
          return {
            success: true,
            message: "删除品类成功"
          };
        } else {
          return {
            success: false,
            message: response.data.message || "删除品类失败"
          };
        }
      } catch (error) {
        formatAppLog("error", "at src/services/categoryService.js:130", "删除品类失败:", error);
        return {
          success: false,
          message: "网络错误，请重试"
        };
      }
    }
    // 根据名称搜索品类
    async searchCategories(keyword) {
      try {
        const response = await request$1.get(this.baseUrl, { name: keyword });
        if (response.data.code === 200) {
          return {
            success: true,
            data: response.data.data.list || []
          };
        } else {
          return {
            success: false,
            message: response.data.message || "搜索品类失败",
            data: []
          };
        }
      } catch (error) {
        formatAppLog("error", "at src/services/categoryService.js:156", "搜索品类失败:", error);
        return {
          success: false,
          message: "网络错误，请重试",
          data: []
        };
      }
    }
    // 获取热门品类（按排序权重）
    async getPopularCategories(limit = 10) {
      try {
        const response = await request$1.get(this.baseUrl, { sort: "sort_order", limit });
        if (response.data.code === 200) {
          return {
            success: true,
            data: response.data.data.list || []
          };
        } else {
          return {
            success: false,
            message: response.data.message || "获取热门品类失败",
            data: []
          };
        }
      } catch (error) {
        formatAppLog("error", "at src/services/categoryService.js:183", "获取热门品类失败:", error);
        return {
          success: false,
          message: "网络错误，请重试",
          data: []
        };
      }
    }
  }
  const categoryService = new CategoryService();
  const _export_sfc = (sfc, props) => {
    const target = sfc.__vccOpts || sfc;
    for (const [key, val] of props) {
      target[key] = val;
    }
    return target;
  };
  const _sfc_main$i = {
    name: "Shop",
    data() {
      return {
        products: [],
        categories: [],
        selectedCategory: "",
        searchKeyword: "",
        sortBy: "created_at",
        sortOrder: "desc",
        page: 1,
        perPage: 16,
        loading: false,
        refreshing: false,
        hasMore: true,
        total: 0
      };
    },
    onLoad() {
      this.fetchCategories();
      this.fetchProducts();
    },
    onShow() {
    },
    methods: {
      // 获取商品品类
      async fetchCategories() {
        try {
          const response = await categoryService.getCategories();
          this.categories = response.data;
        } catch (error) {
          formatAppLog("error", "at pages/shop/shop.vue:145", "获取分类失败:", error);
          uni.showToast({
            title: "获取分类失败",
            icon: "none"
          });
        }
      },
      // 获取商品列表
      async fetchProducts(refresh = false) {
        if (this.loading)
          return;
        this.loading = true;
        if (refresh) {
          this.page = 1;
          this.products = [];
          this.hasMore = true;
        }
        try {
          const params = {
            page: this.page,
            per_page: this.perPage,
            sort_by: this.sortBy,
            sort_order: this.sortOrder
          };
          if (this.selectedCategory) {
            params.category_uuid = this.selectedCategory;
          }
          if (this.searchKeyword) {
            params.search = this.searchKeyword;
          }
          const response = await productApi.getProducts(params);
          if (response.data.code === 200) {
            const { list, total, has_next } = response.data.data;
            if (refresh) {
              this.products = list;
            } else {
              this.products = [...this.products, ...list];
            }
            this.total = total;
            this.hasMore = has_next;
            if (this.refreshing) {
              this.refreshing = false;
            }
          } else {
            uni.showToast({
              title: response.data.message || "获取商品失败",
              icon: "none"
            });
          }
        } catch (error) {
          formatAppLog("error", "at pages/shop/shop.vue:205", "获取商品失败:", error);
          uni.showToast({
            title: "网络错误",
            icon: "none"
          });
        } finally {
          this.loading = false;
        }
      },
      // 选择分类
      selectCategory(categoryId) {
        this.selectedCategory = categoryId;
        this.fetchProducts(true);
      },
      // 搜索
      handleSearch() {
        this.fetchProducts(true);
      },
      // 搜索输入
      handleSearchInput() {
      },
      // 改变排序
      changeSort(sortBy) {
        if (this.sortBy === sortBy) {
          this.sortOrder = this.sortOrder === "asc" ? "desc" : "asc";
        } else {
          this.sortBy = sortBy;
          this.sortOrder = "desc";
        }
        this.fetchProducts(true);
      },
      // 跳转到商品详情
      goToProduct(productId) {
        uni.navigateTo({
          url: `/pages/product-detail/product-detail?id=${productId}`
        });
      },
      // 一键加入购物车（若有规格则默认第一个活动规格组合）
      async quickAdd(item) {
        try {
          const specCombinationId = item.has_specs ? item.default_spec_combination_id : void 0;
          const res = await cartApi.quickAddToCart({
            productId: item.id,
            userId: getUserId(),
            quantity: 1,
            specCombinationId
          });
          if (res.data.code === 200) {
            uni.showToast({
              title: "已加入购物车",
              icon: "success"
            });
          } else {
            uni.showToast({
              title: res.data.message || "加入购物车失败",
              icon: "none"
            });
          }
        } catch (e) {
          formatAppLog("error", "at pages/shop/shop.vue:271", "加入购物车失败:", e);
          uni.showToast({
            title: "网络错误，加入购物车失败",
            icon: "none"
          });
        }
      },
      // 设置滚动监听
      setupScrollListener() {
      },
      // 移除滚动监听
      removeScrollListener() {
      },
      // 处理滚动事件 - 使用uni-app的onReachBottom生命周期
      onReachBottom() {
        if (this.hasMore && !this.loading) {
          this.loadMore();
        }
      },
      // 加载更多
      loadMore() {
        if (this.hasMore && !this.loading) {
          this.page++;
          this.fetchProducts();
        }
      }
    }
  };
  function _sfc_render$h(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "shop-container" }, [
      vue.createCommentVNode(" 搜索栏 "),
      vue.createElementVNode("view", { class: "search-bar" }, [
        vue.createElementVNode("view", { class: "search-input" }, [
          vue.createElementVNode("i", { class: "search-icon" }, "🔍"),
          vue.withDirectives(vue.createElementVNode(
            "input",
            {
              "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => $data.searchKeyword = $event),
              placeholder: "搜索商品",
              onKeyup: _cache[1] || (_cache[1] = vue.withKeys((...args) => $options.handleSearch && $options.handleSearch(...args), ["enter"])),
              onInput: _cache[2] || (_cache[2] = (...args) => $options.handleSearchInput && $options.handleSearchInput(...args))
            },
            null,
            544
            /* NEED_HYDRATION, NEED_PATCH */
          ), [
            [vue.vModelText, $data.searchKeyword]
          ])
        ])
      ]),
      vue.createCommentVNode(" 分类筛选 "),
      vue.createElementVNode("view", { class: "category-filter" }, [
        vue.createElementVNode("view", { class: "category-scroll" }, [
          vue.createElementVNode(
            "view",
            {
              class: vue.normalizeClass(["category-item", { active: $data.selectedCategory === "" }]),
              onClick: _cache[3] || (_cache[3] = ($event) => $options.selectCategory(""))
            },
            " 全部 ",
            2
            /* CLASS */
          ),
          (vue.openBlock(true), vue.createElementBlock(
            vue.Fragment,
            null,
            vue.renderList($data.categories, (category) => {
              return vue.openBlock(), vue.createElementBlock("view", {
                key: category.uuid,
                class: vue.normalizeClass(["category-item", { active: $data.selectedCategory === category.uuid }]),
                onClick: ($event) => $options.selectCategory(category.uuid)
              }, vue.toDisplayString(category.name), 11, ["onClick"]);
            }),
            128
            /* KEYED_FRAGMENT */
          ))
        ])
      ]),
      vue.createCommentVNode(" 排序栏 "),
      vue.createElementVNode("view", { class: "sort-bar" }, [
        vue.createElementVNode(
          "view",
          {
            class: vue.normalizeClass(["sort-item", { active: $data.sortBy === "created_at" }]),
            onClick: _cache[4] || (_cache[4] = ($event) => $options.changeSort("created_at"))
          },
          " 最新 ",
          2
          /* CLASS */
        ),
        vue.createElementVNode(
          "view",
          {
            class: vue.normalizeClass(["sort-item", { active: $data.sortBy === "price" }]),
            onClick: _cache[5] || (_cache[5] = ($event) => $options.changeSort("price"))
          },
          [
            vue.createTextVNode(" 价格 "),
            vue.createElementVNode(
              "i",
              { class: "sort-icon" },
              vue.toDisplayString($data.sortOrder === "asc" ? "↑" : "↓"),
              1
              /* TEXT */
            )
          ],
          2
          /* CLASS */
        ),
        vue.createElementVNode(
          "view",
          {
            class: vue.normalizeClass(["sort-item", { active: $data.sortBy === "sales" }]),
            onClick: _cache[6] || (_cache[6] = ($event) => $options.changeSort("sales"))
          },
          " 销量 ",
          2
          /* CLASS */
        )
      ]),
      vue.createCommentVNode(" 商品列表 "),
      vue.createElementVNode("view", { class: "product-list" }, [
        (vue.openBlock(true), vue.createElementBlock(
          vue.Fragment,
          null,
          vue.renderList($data.products, (item) => {
            return vue.openBlock(), vue.createElementBlock("view", {
              class: "product-item",
              key: item.id,
              onClick: ($event) => $options.goToProduct(item.id)
            }, [
              vue.createElementVNode("image", {
                class: "product-image",
                src: item.images && item.images[0] || item.image_url
              }, null, 8, ["src"]),
              vue.createElementVNode("view", { class: "product-info" }, [
                vue.createElementVNode(
                  "view",
                  { class: "product-title" },
                  vue.toDisplayString(item.name),
                  1
                  /* TEXT */
                ),
                vue.createElementVNode("view", { class: "product-meta" }, [
                  vue.createElementVNode(
                    "text",
                    { class: "category-name" },
                    vue.toDisplayString(item.category_name),
                    1
                    /* TEXT */
                  ),
                  vue.createElementVNode(
                    "text",
                    { class: "sales-count" },
                    "已售" + vue.toDisplayString(item.sales_count || 0) + "件",
                    1
                    /* TEXT */
                  )
                ]),
                vue.createElementVNode("view", { class: "price-section" }, [
                  vue.createElementVNode(
                    "text",
                    { class: "current-price" },
                    "¥" + vue.toDisplayString(item.price),
                    1
                    /* TEXT */
                  ),
                  item.original_price ? (vue.openBlock(), vue.createElementBlock(
                    "text",
                    {
                      key: 0,
                      class: "original-price"
                    },
                    "¥" + vue.toDisplayString(item.original_price),
                    1
                    /* TEXT */
                  )) : vue.createCommentVNode("v-if", true)
                ]),
                vue.createElementVNode("view", { class: "rating-section" }, [
                  vue.createElementVNode("view", { class: "rating-stars" }, [
                    (vue.openBlock(), vue.createElementBlock(
                      vue.Fragment,
                      null,
                      vue.renderList(5, (i) => {
                        return vue.createElementVNode(
                          "text",
                          {
                            key: i,
                            class: vue.normalizeClass(["star", { active: i <= (item.rating || 0) }])
                          },
                          "★",
                          2
                          /* CLASS */
                        );
                      }),
                      64
                      /* STABLE_FRAGMENT */
                    ))
                  ]),
                  vue.createElementVNode(
                    "text",
                    { class: "rating-text" },
                    vue.toDisplayString(item.rating || 0),
                    1
                    /* TEXT */
                  ),
                  vue.createElementVNode(
                    "text",
                    { class: "review-count" },
                    "(" + vue.toDisplayString(item.review_count || 0) + ")",
                    1
                    /* TEXT */
                  )
                ])
              ]),
              vue.createElementVNode("button", {
                class: "cart-icon-btn",
                onClick: vue.withModifiers(($event) => $options.quickAdd(item), ["stop"]),
                "aria-label": "加入购物车"
              }, "+", 8, ["onClick"])
            ], 8, ["onClick"]);
          }),
          128
          /* KEYED_FRAGMENT */
        )),
        vue.createCommentVNode(" 加载更多 "),
        $data.loading ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 0,
          class: "loading"
        }, [
          vue.createElementVNode("view", { class: "loading-text" }, "加载中...")
        ])) : vue.createCommentVNode("v-if", true),
        vue.createCommentVNode(" 没有更多数据 "),
        !$data.hasMore && $data.products.length > 0 ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 1,
          class: "no-more"
        }, [
          vue.createElementVNode("view", { class: "no-more-text" }, "没有更多数据了")
        ])) : vue.createCommentVNode("v-if", true),
        vue.createCommentVNode(" 空状态 "),
        !$data.loading && $data.products.length === 0 ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 2,
          class: "empty-state"
        }, [
          vue.createElementVNode("view", { class: "empty-text" }, "暂无商品")
        ])) : vue.createCommentVNode("v-if", true)
      ])
    ]);
  }
  const PagesShopShop = /* @__PURE__ */ _export_sfc(_sfc_main$i, [["render", _sfc_render$h], ["__scopeId", "data-v-2a6aaf81"], ["__file", "/Users/chenjianping/Desktop/private/pro/sheng/yinjiajia/app/front-app-uni/pages/shop/shop.vue"]]);
  const _sfc_main$h = {
    name: "ConfirmModal",
    props: {
      visible: {
        type: Boolean,
        default: false
      },
      title: {
        type: String,
        default: "确认"
      },
      content: {
        type: String,
        default: ""
      },
      confirmText: {
        type: String,
        default: "确定"
      },
      cancelText: {
        type: String,
        default: "取消"
      },
      type: {
        type: String,
        default: "default"
      }
    },
    computed: {
      typeClass() {
        return `modal-${this.type}`;
      }
    },
    methods: {
      handleConfirm() {
        this.$emit("confirm");
      },
      handleCancel() {
        this.$emit("cancel");
      },
      handleOverlayClick() {
        this.$emit("cancel");
      }
    }
  };
  function _sfc_render$g(_ctx, _cache, $props, $setup, $data, $options) {
    return $props.visible ? (vue.openBlock(), vue.createElementBlock("view", {
      key: 0,
      class: "modal-overlay",
      onClick: _cache[3] || (_cache[3] = (...args) => $options.handleOverlayClick && $options.handleOverlayClick(...args))
    }, [
      vue.createElementVNode(
        "view",
        {
          class: vue.normalizeClass(["modal-content", $options.typeClass]),
          onClick: _cache[2] || (_cache[2] = vue.withModifiers(() => {
          }, ["stop"]))
        },
        [
          vue.createElementVNode("view", { class: "modal-header" }, [
            vue.createElementVNode(
              "text",
              { class: "modal-title" },
              vue.toDisplayString($props.title),
              1
              /* TEXT */
            )
          ]),
          vue.createElementVNode("view", { class: "modal-body" }, [
            vue.createElementVNode(
              "text",
              { class: "modal-message" },
              vue.toDisplayString($props.content),
              1
              /* TEXT */
            )
          ]),
          vue.createElementVNode("view", { class: "modal-footer" }, [
            vue.createElementVNode(
              "button",
              {
                class: "modal-btn cancel-btn",
                onClick: _cache[0] || (_cache[0] = (...args) => $options.handleCancel && $options.handleCancel(...args))
              },
              vue.toDisplayString($props.cancelText),
              1
              /* TEXT */
            ),
            vue.createElementVNode(
              "button",
              {
                class: "modal-btn confirm-btn",
                onClick: _cache[1] || (_cache[1] = (...args) => $options.handleConfirm && $options.handleConfirm(...args))
              },
              vue.toDisplayString($props.confirmText),
              1
              /* TEXT */
            )
          ])
        ],
        2
        /* CLASS */
      )
    ])) : vue.createCommentVNode("v-if", true);
  }
  const ConfirmModal = /* @__PURE__ */ _export_sfc(_sfc_main$h, [["render", _sfc_render$g], ["__scopeId", "data-v-5d0d13a1"], ["__file", "/Users/chenjianping/Desktop/private/pro/sheng/yinjiajia/app/front-app-uni/components/ConfirmModal.vue"]]);
  const _sfc_main$g = {
    __name: "cart",
    setup(__props, { expose: __expose }) {
      __expose();
      const cartList = vue.ref([]);
      const loading = vue.ref(false);
      const longPressTimer = vue.ref(null);
      const longPressItem = vue.ref(null);
      const showConfirmModal = vue.ref(false);
      const confirmModalData = vue.ref({
        title: "",
        content: "",
        item: null
      });
      const userInfo = vue.ref({
        user_id: getUserId()
      });
      const selectedCount = vue.computed(() => {
        return cartList.value.filter((item) => item.selected).length;
      });
      const selectedTotalPrice = vue.computed(() => {
        return cartList.value.reduce((total, item) => {
          return item.selected ? total + item.item_total : total;
        }, 0);
      });
      const isAllSelected = vue.computed(() => {
        return cartList.value.length > 0 && cartList.value.every((item) => item.selected);
      });
      const formatPrice = (price) => {
        return Number(price).toFixed(2);
      };
      const getItemImage = (item) => {
        if (item.spec_combination_id && item.spec_combination_image) {
          return item.spec_combination_image;
        }
        return item.product_image || "https://via.placeholder.com/80x80/f5f5f5/cccccc?text=商品";
      };
      const getSpecText = (item) => {
        if (!item.spec_combination_id)
          return "";
        return `规格: ${item.spec_combination_id}`;
      };
      const showToast = (message) => {
        alert(message);
      };
      const fetchCartList = async () => {
        loading.value = true;
        try {
          const response = await cartApi.getCart(userInfo.value.user_id);
          if (response.data.code === 200) {
            cartList.value = response.data.data.items.map((item) => ({
              ...item,
              selected: false
            }));
          } else {
            showToast(response.data.message || "获取购物车失败");
          }
        } catch (error) {
          formatAppLog("error", "at pages/cart/cart.vue:202", "获取购物车列表失败:", error);
          showToast("网络错误，请重试");
        } finally {
          loading.value = false;
        }
      };
      const toggleSelectAll = () => {
        const newSelectState = !isAllSelected.value;
        cartList.value = cartList.value.map((item) => ({
          ...item,
          selected: newSelectState
        }));
      };
      const toggleSelectItem = (item) => {
        item.selected = !item.selected;
      };
      const increaseQuantity = async (item) => {
        if (item.quantity >= item.stock) {
          showToast("已达到最大库存");
          return;
        }
        try {
          const response = await cartApi.updateCartItem(item.id, {
            quantity: item.quantity + 1,
            user_id: userInfo.value.user_id
          });
          if (response.data.code === 200) {
            item.quantity++;
            item.item_total = item.price * item.quantity;
          } else {
            showToast(response.data.message || "更新数量失败");
          }
        } catch (error) {
          formatAppLog("error", "at pages/cart/cart.vue:244", "更新数量失败:", error);
          showToast("网络错误，请重试");
        }
      };
      const decreaseQuantity = async (item) => {
        if (item.quantity <= 1) {
          return;
        }
        try {
          const response = await cartApi.updateCartItem(item.id, {
            quantity: item.quantity - 1,
            user_id: userInfo.value.user_id
          });
          if (response.data.code === 200) {
            item.quantity--;
            item.item_total = item.price * item.quantity;
          } else {
            showToast(response.data.message || "更新数量失败");
          }
        } catch (error) {
          formatAppLog("error", "at pages/cart/cart.vue:269", "更新数量失败:", error);
        }
      };
      const removeFromCart = async (item) => {
        try {
          const response = await cartApi.removeCartItem(item.id, userInfo.value.user_id);
          if (response.data.code === 200) {
            const index = cartList.value.findIndex((cartItem) => cartItem.id === item.id);
            if (index > -1) {
              cartList.value.splice(index, 1);
            }
          } else {
            showToast(response.data.message || "删除失败");
          }
        } catch (error) {
          formatAppLog("error", "at pages/cart/cart.vue:289", "删除商品失败:", error);
          showToast("网络错误，请重试");
        }
      };
      const clearAllItems = async () => {
        try {
          const response = await cartApi.clearCart(userInfo.value.user_id);
          if (response.data.code === 200) {
            cartList.value = [];
          } else {
            showToast(response.data.message || "清空购物车失败");
          }
        } catch (error) {
          formatAppLog("error", "at pages/cart/cart.vue:306", "清空购物车失败:", error);
          showToast("网络错误，请重试");
        }
      };
      const goToPay = () => {
        const selectedItems = cartList.value.filter((item) => item.selected);
        if (selectedItems.length === 0) {
          showToast("请选择至少一个商品");
          return;
        }
        selectedItems.reduce((total, item) => {
          return total + item.item_total;
        }, 0);
        const cartItemIds = selectedItems.map((item) => item.id).join(",");
        uni.navigateTo({
          url: `/pages/checkout/checkout?cart_items=${cartItemIds}`
        });
      };
      const startLongPress = (item) => {
        longPressItem.value = item;
        longPressTimer.value = setTimeout(() => {
          confirmModalData.value = {
            title: "确认删除",
            content: `确定要删除"${item.product_name}"吗？`,
            item
          };
          showConfirmModal.value = true;
        }, 1e3);
      };
      const endLongPress = () => {
        if (longPressTimer.value) {
          clearTimeout(longPressTimer.value);
          longPressTimer.value = null;
        }
        longPressItem.value = null;
      };
      const handleConfirmDelete = () => {
        if (confirmModalData.value.item) {
          removeFromCart(confirmModalData.value.item);
        }
        showConfirmModal.value = false;
        confirmModalData.value = { title: "", content: "", item: null };
      };
      const handleCancelDelete = () => {
        showConfirmModal.value = false;
        confirmModalData.value = { title: "", content: "", item: null };
      };
      const goToShop = () => {
        uni.switchTab({
          url: "/pages/shop/shop"
        });
      };
      vue.onMounted(() => {
        fetchCartList();
      });
      const __returned__ = { cartList, loading, longPressTimer, longPressItem, showConfirmModal, confirmModalData, userInfo, selectedCount, selectedTotalPrice, isAllSelected, formatPrice, getItemImage, getSpecText, showToast, fetchCartList, toggleSelectAll, toggleSelectItem, increaseQuantity, decreaseQuantity, removeFromCart, clearAllItems, goToPay, startLongPress, endLongPress, handleConfirmDelete, handleCancelDelete, goToShop, ref: vue.ref, computed: vue.computed, onMounted: vue.onMounted, get cartApi() {
        return cartApi;
      }, get getUserId() {
        return getUserId;
      }, ConfirmModal };
      Object.defineProperty(__returned__, "__isScriptSetup", { enumerable: false, value: true });
      return __returned__;
    }
  };
  function _sfc_render$f(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "cart-container" }, [
      vue.createCommentVNode(" 页面头部 "),
      vue.createElementVNode("view", { class: "cart-header" }, [
        vue.createElementVNode("h1", { class: "page-title" }, "购物车"),
        vue.createElementVNode(
          "text",
          { class: "item-count" },
          vue.toDisplayString($setup.cartList.length) + "件商品",
          1
          /* TEXT */
        )
      ]),
      vue.createCommentVNode(" 购物车为空状态 "),
      $setup.cartList.length === 0 ? (vue.openBlock(), vue.createElementBlock("view", {
        key: 0,
        class: "empty-cart"
      }, [
        vue.createElementVNode("view", { class: "empty-text" }, "购物车空空如也"),
        vue.createElementVNode("view", {
          class: "shop-btn",
          onClick: $setup.goToShop
        }, "去购物")
      ])) : (vue.openBlock(), vue.createElementBlock(
        vue.Fragment,
        { key: 1 },
        [
          vue.createCommentVNode(" 购物车列表 "),
          vue.createElementVNode("view", { class: "cart-content" }, [
            vue.createCommentVNode(" 商品列表 "),
            vue.createElementVNode("view", { class: "cart-items" }, [
              (vue.openBlock(true), vue.createElementBlock(
                vue.Fragment,
                null,
                vue.renderList($setup.cartList, (item, index) => {
                  return vue.openBlock(), vue.createElementBlock("view", {
                    key: item.id,
                    class: vue.normalizeClass(["cart-item", { "item-selected": item.selected }]),
                    onTouchstart: ($event) => $setup.startLongPress(item),
                    onTouchend: $setup.endLongPress,
                    onTouchcancel: $setup.endLongPress,
                    onMousedown: ($event) => $setup.startLongPress(item),
                    onMouseup: $setup.endLongPress,
                    onMouseleave: $setup.endLongPress
                  }, [
                    vue.createCommentVNode(" 选择框 "),
                    vue.createElementVNode("view", {
                      class: "item-select",
                      onClick: ($event) => $setup.toggleSelectItem(item)
                    }, [
                      vue.createElementVNode(
                        "view",
                        {
                          class: vue.normalizeClass(["checkbox-custom", { "checked": item.selected }])
                        },
                        [
                          item.selected ? (vue.openBlock(), vue.createElementBlock("text", {
                            key: 0,
                            class: "check-icon"
                          }, "✓")) : vue.createCommentVNode("v-if", true)
                        ],
                        2
                        /* CLASS */
                      )
                    ], 8, ["onClick"]),
                    vue.createCommentVNode(" 商品信息 "),
                    vue.createElementVNode("view", { class: "item-info" }, [
                      vue.createElementVNode("view", { class: "item-image" }, [
                        vue.createElementVNode("image", {
                          src: $setup.getItemImage(item)
                        }, null, 8, ["src"])
                      ]),
                      vue.createElementVNode("view", { class: "item-details" }, [
                        vue.createElementVNode("h3", {
                          class: "item-name",
                          title: item.product_name
                        }, vue.toDisplayString(item.product_name), 9, ["title"]),
                        vue.createCommentVNode(" 显示规格信息 "),
                        item.spec_combination_id ? (vue.openBlock(), vue.createElementBlock("view", {
                          key: 0,
                          class: "item-specs"
                        }, [
                          vue.createElementVNode(
                            "text",
                            { class: "spec-text" },
                            vue.toDisplayString($setup.getSpecText(item)),
                            1
                            /* TEXT */
                          )
                        ])) : vue.createCommentVNode("v-if", true),
                        vue.createElementVNode(
                          "view",
                          { class: "item-price" },
                          "¥" + vue.toDisplayString($setup.formatPrice(item.price)),
                          1
                          /* TEXT */
                        )
                      ])
                    ]),
                    vue.createCommentVNode(" 数量控制 "),
                    vue.createElementVNode("view", { class: "quantity-control" }, [
                      vue.createElementVNode("button", {
                        class: "quantity-btn minus",
                        onClick: ($event) => $setup.decreaseQuantity(item),
                        disabled: item.quantity <= 1
                      }, [
                        vue.createElementVNode("text", null, "-")
                      ], 8, ["onClick", "disabled"]),
                      vue.createElementVNode(
                        "text",
                        { class: "quantity-display" },
                        vue.toDisplayString(item.quantity),
                        1
                        /* TEXT */
                      ),
                      vue.createElementVNode("button", {
                        class: "quantity-btn plus",
                        onClick: ($event) => $setup.increaseQuantity(item),
                        disabled: item.quantity >= item.stock
                      }, [
                        vue.createElementVNode("text", null, "+")
                      ], 8, ["onClick", "disabled"])
                    ])
                  ], 42, ["onTouchstart", "onMousedown"]);
                }),
                128
                /* KEYED_FRAGMENT */
              ))
            ]),
            vue.createCommentVNode(" 底部结算区域 "),
            vue.createElementVNode("view", { class: "cart-footer" }, [
              vue.createCommentVNode(" 全选区域 "),
              vue.createElementVNode("view", {
                class: "select-all-section",
                onClick: $setup.toggleSelectAll
              }, [
                vue.createElementVNode("view", { class: "select-all-label" }, [
                  vue.createElementVNode(
                    "view",
                    {
                      class: vue.normalizeClass(["checkbox-custom", { "checked": $setup.isAllSelected }])
                    },
                    [
                      $setup.isAllSelected ? (vue.openBlock(), vue.createElementBlock("text", {
                        key: 0,
                        class: "check-icon"
                      }, "✓")) : vue.createCommentVNode("v-if", true)
                    ],
                    2
                    /* CLASS */
                  ),
                  vue.createElementVNode("text", { class: "select-text" }, "全选")
                ])
              ]),
              vue.createCommentVNode(" 合计信息 "),
              vue.createElementVNode("view", { class: "total-info" }, [
                vue.createElementVNode("text", { class: "total-label" }, "合计："),
                vue.createElementVNode(
                  "text",
                  { class: "total-amount" },
                  "¥" + vue.toDisplayString($setup.formatPrice($setup.selectedTotalPrice)),
                  1
                  /* TEXT */
                ),
                vue.createElementVNode(
                  "text",
                  { class: "selected-count" },
                  "(" + vue.toDisplayString($setup.selectedCount) + "件)",
                  1
                  /* TEXT */
                )
              ]),
              vue.createCommentVNode(" 结算按钮 "),
              vue.createElementVNode("view", { class: "checkout-section" }, [
                vue.createElementVNode("view", {
                  class: vue.normalizeClass(["checkout-btn", { "disabled": $setup.selectedCount === 0 }]),
                  onClick: $setup.goToPay,
                  disabled: $setup.selectedCount === 0
                }, " 结算 (" + vue.toDisplayString($setup.selectedCount) + ") ", 11, ["disabled"])
              ])
            ])
          ])
        ],
        2112
        /* STABLE_FRAGMENT, DEV_ROOT_FRAGMENT */
      )),
      vue.createCommentVNode(" 加载状态 "),
      $setup.loading ? (vue.openBlock(), vue.createElementBlock("view", {
        key: 2,
        class: "loading-overlay"
      }, [
        vue.createElementVNode("view", { class: "loading-spinner" }),
        vue.createElementVNode("p", null, "加载中...")
      ])) : vue.createCommentVNode("v-if", true),
      vue.createCommentVNode(" 确认删除模态框 "),
      vue.createVNode($setup["ConfirmModal"], {
        visible: $setup.showConfirmModal,
        title: $setup.confirmModalData.title,
        content: $setup.confirmModalData.content,
        type: "delete",
        onConfirm: $setup.handleConfirmDelete,
        onCancel: $setup.handleCancelDelete
      }, null, 8, ["visible", "title", "content"])
    ]);
  }
  const PagesCartCart = /* @__PURE__ */ _export_sfc(_sfc_main$g, [["render", _sfc_render$f], ["__scopeId", "data-v-c91e7611"], ["__file", "/Users/chenjianping/Desktop/private/pro/sheng/yinjiajia/app/front-app-uni/pages/cart/cart.vue"]]);
  const _sfc_main$f = {
    name: "Profile",
    components: {
      ConfirmModal
    },
    data() {
      return {
        userInfo: getUser(),
        showLogoutModal: false
      };
    },
    computed: {
      displayName() {
        if (this.userInfo && (this.userInfo.phone || this.userInfo.user_number)) {
          return this.userInfo.phone || `用户${this.userInfo.user_number}`;
        }
        return "未登录";
      },
      userIdDisplay() {
        if (this.userInfo && (this.userInfo.user_number || this.userInfo.user_id)) {
          return this.userInfo.user_number || this.userInfo.user_id;
        }
        return "--";
      }
    },
    methods: {
      goToOrders() {
        uni.navigateTo({
          url: "/pages/myorder/myorder"
        });
      },
      goToAddress() {
        uni.navigateTo({
          url: "/pages/address/address"
        });
      },
      goToCustomerService() {
        uni.navigateTo({
          url: "/pages/customer-service/customer-service"
        });
      },
      goToSettings() {
        uni.showToast({
          icon: "error",
          title: "设置功能开发中..."
        });
      },
      goToAbout() {
        uni.showToast({
          icon: "error",
          title: "关于我们功能开发中..."
        });
      },
      showLogoutConfirm() {
        this.showLogoutModal = true;
      },
      handleLogoutConfirm() {
        clearToken();
        clearUser();
        this.userInfo = {};
        this.showLogoutModal = false;
        uni.navigateTo({
          url: "/pages/login/login"
        });
      }
    }
  };
  function _sfc_render$e(_ctx, _cache, $props, $setup, $data, $options) {
    const _component_ConfirmModal = vue.resolveComponent("ConfirmModal");
    return vue.openBlock(), vue.createElementBlock("view", { class: "profile-container" }, [
      vue.createCommentVNode(" 用户信息区域 "),
      vue.createElementVNode("view", { class: "user-info-section" }, [
        vue.createElementVNode("view", { class: "user-avatar" }, [
          vue.createElementVNode("view", { class: "avatar-placeholder" }, "��")
        ]),
        vue.createElementVNode("view", { class: "user-details" }, [
          vue.createElementVNode(
            "view",
            { class: "username" },
            vue.toDisplayString($options.displayName),
            1
            /* TEXT */
          ),
          vue.createElementVNode(
            "view",
            { class: "user-id" },
            "ID: " + vue.toDisplayString($options.userIdDisplay),
            1
            /* TEXT */
          )
        ]),
        vue.createElementVNode("view", {
          class: "settings-btn",
          onClick: _cache[0] || (_cache[0] = (...args) => $options.goToSettings && $options.goToSettings(...args))
        }, [
          vue.createElementVNode("text", null, "⚙️")
        ])
      ]),
      vue.createCommentVNode(" 功能菜单 "),
      vue.createElementVNode("view", { class: "menu-section" }, [
        vue.createCommentVNode(" 订单相关 "),
        vue.createElementVNode("view", { class: "menu-group" }, [
          vue.createElementVNode("view", {
            class: "menu-item",
            onClick: _cache[1] || (_cache[1] = (...args) => $options.goToOrders && $options.goToOrders(...args))
          }, [
            vue.createElementVNode("view", { class: "menu-content" }, [
              vue.createElementVNode("view", { class: "menu-title" }, "我的订单"),
              vue.createElementVNode("view", { class: "menu-desc" }, "查看所有订单状态")
            ]),
            vue.createElementVNode("view", { class: "menu-arrow" }, ">")
          ]),
          vue.createElementVNode("view", {
            class: "menu-item",
            onClick: _cache[2] || (_cache[2] = (...args) => $options.goToAddress && $options.goToAddress(...args))
          }, [
            vue.createElementVNode("view", { class: "menu-content" }, [
              vue.createElementVNode("view", { class: "menu-title" }, "收货地址"),
              vue.createElementVNode("view", { class: "menu-desc" }, "管理收货地址")
            ]),
            vue.createElementVNode("view", { class: "menu-arrow" }, ">")
          ])
        ]),
        vue.createCommentVNode(" 其他功能 "),
        vue.createElementVNode("view", { class: "menu-group" }, [
          vue.createElementVNode("view", {
            class: "menu-item",
            onClick: _cache[3] || (_cache[3] = (...args) => $options.goToCustomerService && $options.goToCustomerService(...args))
          }, [
            vue.createElementVNode("view", { class: "menu-content" }, [
              vue.createElementVNode("view", { class: "menu-title" }, "客服中心"),
              vue.createElementVNode("view", { class: "menu-desc" }, "联系客服解决问题")
            ]),
            vue.createElementVNode("view", { class: "menu-arrow" }, ">")
          ]),
          vue.createElementVNode("view", {
            class: "menu-item",
            onClick: _cache[4] || (_cache[4] = (...args) => $options.goToAbout && $options.goToAbout(...args))
          }, [
            vue.createElementVNode("view", { class: "menu-content" }, [
              vue.createElementVNode("view", { class: "menu-title" }, "关于我们"),
              vue.createElementVNode("view", { class: "menu-desc" }, "了解更多信息")
            ]),
            vue.createElementVNode("view", { class: "menu-arrow" }, ">")
          ])
        ]),
        vue.createCommentVNode(" 退出登录 "),
        vue.createElementVNode("view", { class: "menu-group" }, [
          vue.createElementVNode("view", {
            class: "menu-item logout-item",
            onClick: _cache[5] || (_cache[5] = (...args) => $options.showLogoutConfirm && $options.showLogoutConfirm(...args))
          }, [
            vue.createElementVNode("view", { class: "menu-content" }, [
              vue.createElementVNode("view", { class: "menu-title" }, "退出登录"),
              vue.createElementVNode("view", { class: "menu-desc" }, "安全退出当前账号")
            ]),
            vue.createElementVNode("view", { class: "menu-arrow" }, ">")
          ])
        ])
      ]),
      vue.createCommentVNode(" 自定义确认弹窗 "),
      vue.createVNode(_component_ConfirmModal, {
        visible: $data.showLogoutModal,
        title: "确认退出",
        content: "确定要退出登录吗？",
        "confirm-text": "退出登录",
        "cancel-text": "取消",
        type: "logout",
        onConfirm: $options.handleLogoutConfirm,
        onCancel: _cache[6] || (_cache[6] = ($event) => $data.showLogoutModal = false)
      }, null, 8, ["visible", "onConfirm"])
    ]);
  }
  const PagesProfileProfile = /* @__PURE__ */ _export_sfc(_sfc_main$f, [["render", _sfc_render$e], ["__scopeId", "data-v-dd383ca2"], ["__file", "/Users/chenjianping/Desktop/private/pro/sheng/yinjiajia/app/front-app-uni/pages/profile/profile.vue"]]);
  const _sfc_main$e = {
    data() {
      return {
        message: "",
        showEmoji: false,
        scrollToView: "",
        messages: [
          {
            type: "cs",
            text: "您好，音加加客服为您服务，请问有什么可以帮您？",
            time: "10:30"
          },
          {
            type: "user",
            text: "我买的iPhone 13什么时候能发货？",
            time: "10:32"
          }
          // 更多消息...
        ]
      };
    },
    methods: {
      goBack() {
        uni.navigateBack();
      },
      sendMessage() {
        if (!this.message.trim())
          return;
        this.messages.push({
          type: "user",
          text: this.message,
          time: this.getCurrentTime()
        });
        setTimeout(() => {
          this.messages.push({
            type: "cs",
            text: "您的订单将在24小时内发货，请耐心等待。",
            time: this.getCurrentTime()
          });
          this.scrollToBottom();
        }, 1e3);
        this.message = "";
        this.scrollToBottom();
      },
      toggleEmoji() {
        this.showEmoji = !this.showEmoji;
      },
      scrollToBottom() {
        this.scrollToView = "msg-" + (this.messages.length - 1);
      },
      getCurrentTime() {
        const now = /* @__PURE__ */ new Date();
        return `${now.getHours()}:${now.getMinutes().toString().padStart(2, "0")}`;
      }
    },
    onReady() {
      this.scrollToBottom();
    }
  };
  function _sfc_render$d(_ctx, _cache, $props, $setup, $data, $options) {
    const _component_uni_icons = vue.resolveComponent("uni-icons");
    return vue.openBlock(), vue.createElementBlock("view", { class: "customer-service-container" }, [
      vue.createCommentVNode(" 客服头部 "),
      vue.createElementVNode("view", { class: "cs-header" }, [
        vue.createElementVNode("view", { class: "cs-info" }, [
          vue.createElementVNode("image", {
            class: "cs-avatar",
            src: "https://img10.360buyimg.com/img/s80x80_jfs/t1/123456/32/12345/67890/5f6789abE12345678/abcdef123456.jpg"
          }),
          vue.createElementVNode("view", { class: "cs-meta" }, [
            vue.createElementVNode("text", { class: "cs-name" }, "音加加客服"),
            vue.createElementVNode("text", { class: "cs-status" }, "在线")
          ])
        ]),
        vue.createVNode(_component_uni_icons, {
          type: "close",
          size: "24",
          color: "#999",
          onClick: $options.goBack
        }, null, 8, ["onClick"])
      ]),
      vue.createCommentVNode(" 聊天区域 "),
      vue.createElementVNode("scroll-view", {
        class: "chat-area",
        "scroll-y": "",
        "scroll-into-view": $data.scrollToView
      }, [
        vue.createElementVNode("view", { class: "chat-date" }, "今天 10:30"),
        vue.createCommentVNode(" 客服消息 "),
        vue.createElementVNode("view", { class: "chat-message cs-message" }, [
          vue.createElementVNode("image", {
            class: "avatar",
            src: "https://img10.360buyimg.com/img/s80x80_jfs/t1/123456/32/12345/67890/5f6789abE12345678/abcdef123456.jpg"
          }),
          vue.createElementVNode("view", { class: "message-content" }, [
            vue.createElementVNode("text", { class: "message-text" }, "您好，音加加客服为您服务，请问有什么可以帮您？"),
            vue.createElementVNode("text", { class: "message-time" }, "10:30")
          ])
        ]),
        vue.createCommentVNode(" 用户消息 "),
        vue.createElementVNode("view", { class: "chat-message user-message" }, [
          vue.createElementVNode("view", { class: "message-content" }, [
            vue.createElementVNode("text", { class: "message-text" }, "我买的iPhone 13什么时候能发货？"),
            vue.createElementVNode("text", { class: "message-time" }, "10:32")
          ]),
          vue.createElementVNode("image", {
            class: "avatar",
            src: "https://img10.360buyimg.com/img/s80x80_jfs/t1/123456/32/12345/67890/5f6789abE12345678/abcdef123456.jpg"
          })
        ]),
        vue.createCommentVNode(" 更多消息... ")
      ], 8, ["scroll-into-view"]),
      vue.createCommentVNode(" 输入区域 "),
      vue.createElementVNode("view", { class: "input-area" }, [
        vue.createElementVNode("view", { class: "input-box" }, [
          vue.withDirectives(vue.createElementVNode(
            "input",
            {
              class: "message-input",
              type: "text",
              "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => $data.message = $event),
              placeholder: "请输入消息内容",
              onConfirm: _cache[1] || (_cache[1] = (...args) => $options.sendMessage && $options.sendMessage(...args))
            },
            null,
            544
            /* NEED_HYDRATION, NEED_PATCH */
          ), [
            [vue.vModelText, $data.message]
          ]),
          vue.createElementVNode("view", {
            class: "emoji-btn",
            onClick: _cache[2] || (_cache[2] = (...args) => $options.toggleEmoji && $options.toggleEmoji(...args))
          }, [
            vue.createVNode(_component_uni_icons, {
              type: "happy",
              size: "24",
              color: "#666"
            })
          ])
        ]),
        vue.createElementVNode("view", {
          class: "send-btn",
          onClick: _cache[3] || (_cache[3] = (...args) => $options.sendMessage && $options.sendMessage(...args))
        }, "发送")
      ]),
      vue.createCommentVNode(" 表情面板 "),
      vue.withDirectives(vue.createElementVNode(
        "view",
        { class: "emoji-panel" },
        [
          vue.createCommentVNode(" 这里可以添加表情选择器 ")
        ],
        512
        /* NEED_PATCH */
      ), [
        [vue.vShow, $data.showEmoji]
      ])
    ]);
  }
  const PagesCustomerServiceCustomerService = /* @__PURE__ */ _export_sfc(_sfc_main$e, [["render", _sfc_render$d], ["__scopeId", "data-v-c99b40e2"], ["__file", "/Users/chenjianping/Desktop/private/pro/sheng/yinjiajia/app/front-app-uni/pages/customer-service/customer-service.vue"]]);
  class AddressService {
    /**
     * 获取用户默认地址
     * 优先从本地存储获取，如果没有则从后端API获取并缓存
     * @param {number} userId - 用户ID
     * @returns {Promise<Object|null>} 默认地址对象或null
     */
    static async getDefaultAddress(userId) {
      try {
        const uid = userId || getUserId();
        const cachedAddress = this.getSelectedAddress();
        if (cachedAddress) {
          return cachedAddress;
        }
        const response = await request$1.get("/api/app/address/default", {
          params: { user_id: uid }
        });
        if (response.data.code === 200 && response.data.data) {
          const defaultAddress = response.data.data;
          this.setSelectedAddress(defaultAddress);
          return defaultAddress;
        } else {
          formatAppLog("error", "at src/services/addressService.js:36", "获取默认地址失败:", response.data.message);
          return null;
        }
      } catch (error) {
        formatAppLog("error", "at src/services/addressService.js:40", "获取默认地址异常:", error);
        return null;
      }
    }
    /**
     * 设置选中的地址到本地存储
     * @param {Object} address - 地址对象
     */
    static setSelectedAddress(address) {
      try {
        const uid = getUserId();
        if (address && uid) {
          uni.setStorageSync(`selectedAddress:${uid}`, JSON.stringify(address));
        }
      } catch (error) {
        formatAppLog("error", "at src/services/addressService.js:57", "保存地址到本地存储失败:", error);
      }
    }
    /**
     * 清除选中的地址本地存储
     */
    static clearSelectedAddress() {
      try {
        const uid = getUserId();
        if (uid) {
          uni.removeStorageSync(`selectedAddress:${uid}`);
        }
      } catch (error) {
        formatAppLog("error", "at src/services/addressService.js:71", "清除地址本地存储失败:", error);
      }
    }
    /**
     * 从本地存储获取选中的地址
     * @returns {Object|null} 地址对象或null
     */
    static getSelectedAddress() {
      try {
        const uid = getUserId();
        if (!uid)
          return null;
        const cachedAddress = uni.getStorageSync(`selectedAddress:${uid}`);
        if (cachedAddress) {
          return JSON.parse(cachedAddress);
        }
      } catch (error) {
        formatAppLog("error", "at src/services/addressService.js:89", "获取地址本地存储失败:", error);
        this.clearSelectedAddress();
      }
      return null;
    }
    /**
     * 获取用户所有地址
     * @param {number} userId - 用户ID
     * @returns {Promise<Array>} 地址列表
     */
    static async getUserAddresses(userId) {
      try {
        const uid = userId || getUserId();
        const response = await request$1.get("/api/app/address/", {
          params: { user_id: uid }
        });
        if (response.data.code === 200) {
          return response.data.data || [];
        } else {
          formatAppLog("error", "at src/services/addressService.js:111", "获取地址列表失败:", response.data.message);
          return [];
        }
      } catch (error) {
        formatAppLog("error", "at src/services/addressService.js:115", "获取地址列表异常:", error);
        return [];
      }
    }
    /**
     * 添加新地址
     * @param {Object} addressData - 地址数据
     * @returns {Promise<Object|null>} 添加结果
     */
    static async addAddress(addressData) {
      try {
        const uid = getUserId();
        if (!uid) {
          throw new Error("用户未登录");
        }
        const response = await request$1.post("/api/app/address/", {
          ...addressData,
          user_id: uid
        });
        if (response.data.code === 200) {
          return response.data.data;
        } else {
          throw new Error(response.data.message || "添加地址失败");
        }
      } catch (error) {
        formatAppLog("error", "at src/services/addressService.js:143", "添加地址失败:", error);
        throw error;
      }
    }
    /**
     * 更新地址
     * @param {number} addressId - 地址ID
     * @param {Object} addressData - 地址数据
     * @returns {Promise<Object|null>} 更新结果
     */
    static async updateAddress(addressId, addressData) {
      try {
        const uid = getUserId();
        if (!uid) {
          throw new Error("用户未登录");
        }
        const response = await request$1.put(`/api/app/address/${addressId}`, {
          ...addressData,
          user_id: uid
        });
        if (response.data.code === 200) {
          return response.data.data;
        } else {
          throw new Error(response.data.message || "更新地址失败");
        }
      } catch (error) {
        formatAppLog("error", "at src/services/addressService.js:172", "更新地址失败:", error);
        throw error;
      }
    }
    /**
     * 删除地址
     * @param {number} addressId - 地址ID
     * @returns {Promise<boolean>} 删除结果
     */
    static async deleteAddress(addressId) {
      try {
        const uid = getUserId();
        if (!uid) {
          throw new Error("用户未登录");
        }
        const response = await request$1.delete(`/api/app/address/${addressId}`);
        if (response.data.code === 200) {
          return true;
        } else {
          throw new Error(response.data.message || "删除地址失败");
        }
      } catch (error) {
        formatAppLog("error", "at src/services/addressService.js:197", "删除地址失败:", error);
        throw error;
      }
    }
    /**
     * 设置默认地址
     * @param {number} addressId - 地址ID
     * @returns {Promise<boolean>} 设置结果
     */
    static async setDefaultAddress(addressId) {
      try {
        const uid = getUserId();
        if (!uid) {
          throw new Error("用户未登录");
        }
        const response = await request$1.put(`/api/app/address/${addressId}/default`, {
          user_id: uid
        });
        if (response.data.code === 200) {
          return true;
        } else {
          throw new Error(response.data.message || "设置默认地址失败");
        }
      } catch (error) {
        formatAppLog("error", "at src/services/addressService.js:224", "设置默认地址失败:", error);
        throw error;
      }
    }
    /**
     * 验证地址数据
     * @param {Object} addressData - 地址数据
     * @returns {Object} 验证结果 { isValid: boolean, errors: Array }
     */
    static validateAddress(addressData) {
      const errors = [];
      if (!addressData.receiver_name || addressData.receiver_name.trim() === "") {
        errors.push("收货人姓名不能为空");
      }
      if (!addressData.phone || !/^1[3-9]\d{9}$/.test(addressData.phone)) {
        errors.push("请输入正确的手机号码");
      }
      if (!addressData.province || addressData.province.trim() === "") {
        errors.push("省份不能为空");
      }
      if (!addressData.city || addressData.city.trim() === "") {
        errors.push("城市不能为空");
      }
      if (!addressData.district || addressData.district.trim() === "") {
        errors.push("区县不能为空");
      }
      if (!addressData.detail_address || addressData.detail_address.trim() === "") {
        errors.push("详细地址不能为空");
      }
      return {
        isValid: errors.length === 0,
        errors
      };
    }
  }
  const _sfc_main$d = {
    name: "ProductDetail",
    data() {
      return {
        productId: null,
        currentTab: 0,
        currentImageIndex: 0,
        tabs: ["商品", "评价", "详情", "推荐"],
        product: {
          id: "",
          name: "",
          description: "",
          detail: "",
          price: 0,
          original_price: 0,
          discount: 0,
          stock: 0,
          images: [],
          tags: [],
          specs: [],
          spec_combinations: [],
          has_specs: false,
          review_count: 0,
          positive_rate: 98,
          top_review: null,
          rating: 0,
          sales_count: 0,
          category_name: "",
          merchant_name: ""
        },
        selectedSpecs: {},
        selectedSpec: "",
        selectedCombination: null,
        quantity: 1,
        cartCount: 0,
        _isFetchingCart: false,
        _lastCartFetchAt: 0,
        showPopup: false,
        loading: false,
        selectedAddress: null
        // 新增：用于存储选中的收货地址
      };
    },
    computed: {
      // 检查是否可以确认购买
      canConfirm() {
        if (this.product.has_specs && this.product.specs && this.product.specs.length > 0) {
          return Object.keys(this.selectedSpecs).length === this.product.specs.length && this.selectedCombination;
        }
        return true;
      },
      // 确认按钮文本
      confirmButtonText() {
        if (this.product.has_specs && this.product.specs && this.product.specs.length > 0) {
          return Object.keys(this.selectedSpecs).length === this.product.specs.length && this.selectedCombination ? "确定购买" : "请选择规格";
        }
        return "确定购买";
      },
      // 当前选中规格的价格
      currentPrice() {
        if (this.selectedCombination) {
          return this.selectedCombination.price;
        }
        return this.product.price;
      },
      // 当前选中规格的库存
      currentStock() {
        if (this.selectedCombination) {
          return this.selectedCombination.stock;
        }
        return this.product.stock;
      },
      // 当前选中规格的图片
      currentImage() {
        if (this.selectedCombination && this.selectedCombination.image_url) {
          return this.selectedCombination.image_url;
        }
        return this.product.images && this.product.images[0] || "/static/default-product.png";
      },
      // 商品轮播图数据
      productImages() {
        return this.product.images || ["https://via.placeholder.com/400x300?text=商品图片"];
      },
      // 已选规格文本
      selectedSpecText() {
        const selected = [];
        for (const name in this.selectedSpecs) {
          selected.push(this.selectedSpecs[name]);
        }
        return selected.join(" ");
      }
    },
    onLoad(options) {
      if (options.id) {
        this.productId = options.id;
      }
      this.fetchProductDetail();
      this.fetchCartCount();
      this.loadAddressInfo();
      const cached = AddressService.getSelectedAddress();
      if (cached) {
        this.selectedAddress = cached;
      }
    },
    activated() {
      this.loadAddressInfo();
    },
    methods: {
      // 获取商品详情
      async fetchProductDetail() {
        if (!this.productId)
          return;
        this.loading = true;
        try {
          const response = await productApi.getProductDetail(this.productId);
          if (response.data.code === 200) {
            const productData = response.data.data;
            if (productData.image_url) {
              const images = productData.image_url.split("$%%$");
              productData.images = images.filter((img) => img.trim());
            } else {
              productData.images = [];
            }
            if (productData.has_specs && productData.specs) {
              productData.specs = productData.specs.map((spec) => ({
                ...spec,
                values: Array.isArray(spec.values) ? spec.values : JSON.parse(spec.values || "[]")
              }));
            }
            if (productData.has_specs && productData.spec_combinations) {
              productData.spec_combinations = productData.spec_combinations.map((combo) => ({
                ...combo,
                spec_values: typeof combo.spec_values === "string" ? JSON.parse(combo.spec_values) : combo.spec_values
              }));
            }
            this.product = productData;
            if (this.product.has_specs && this.product.specs && this.product.specs.length > 0) {
              this.selectDefaultSpecs();
            }
          } else {
            uni.showToast({
              title: response.data.message || "获取商品详情失败",
              icon: "error"
            });
          }
        } catch (error) {
          formatAppLog("error", "at pages/product-detail/product-detail.vue:412", "获取商品详情失败:", error);
          uni.showToast({
            title: "网络错误",
            icon: "error"
          });
        } finally {
          this.loading = false;
        }
      },
      // 选择默认规格
      selectDefaultSpecs() {
        if (this.product.specs && this.product.specs.length > 0) {
          this.product.specs.forEach((spec) => {
            if (spec.values && spec.values.length > 0) {
              this.selectedSpecs[spec.name] = spec.values[0];
            }
          });
          this.updateSelectedSpecText();
          this.findMatchingCombination();
        }
      },
      // 获取购物车数量
      async fetchCartCount() {
        var _a;
        const now = Date.now();
        if (this._isFetchingCart || now - this._lastCartFetchAt < 500)
          return;
        this._isFetchingCart = true;
        try {
          const response = await cartApi.getCart(getUserId());
          if (response.data.code === 200) {
            const data = response.data.data;
            this.cartCount = data && (data.item_count || (((_a = data.items) == null ? void 0 : _a.length) ?? 0)) || 0;
          }
        } catch (error) {
          formatAppLog("error", "at pages/product-detail/product-detail.vue:449", "获取购物车数量失败:", error);
        } finally {
          this._isFetchingCart = false;
          this._lastCartFetchAt = now;
        }
      },
      // 加载地址信息
      async loadAddressInfo() {
        this.selectedAddress = await AddressService.getDefaultAddress(getUserId());
      },
      // 返回上一页
      goBack() {
        uni.navigateBack();
      },
      // 切换标签
      switchTab(index) {
        this.currentTab = index;
      },
      // 预览图片
      previewImage(index) {
        uni.previewImage({
          current: this.productImages[index],
          urls: this.productImages
        });
      },
      // 上一张图片
      prevImage() {
        if (this.productImages.length > 1) {
          this.currentImageIndex = this.currentImageIndex > 0 ? this.currentImageIndex - 1 : this.productImages.length - 1;
        }
      },
      // 下一张图片
      nextImage() {
        if (this.productImages.length > 1) {
          this.currentImageIndex = this.currentImageIndex < this.productImages.length - 1 ? this.currentImageIndex + 1 : 0;
        }
      },
      // 跳转到指定图片
      goToImage(index) {
        this.currentImageIndex = index;
      },
      // 预览评价图片
      previewReviewImage(index) {
        if (this.product.top_review && this.product.top_review.images) {
          formatAppLog("log", "at pages/product-detail/product-detail.vue:504", "预览评价图片:", this.product.top_review.images[index]);
        }
      },
      // 分享商品
      shareProduct() {
        if (this.product.name) {
          uni.showToast({
            title: "商品已分享",
            icon: "success"
          });
        }
      },
      // 跳转到评价页面
      goToReviews() {
        uni.navigateTo({
          url: `/pages/reviews/reviews?id=${this.productId}`
        });
      },
      // 显示规格选择弹窗
      showSpecPopup() {
        this.showPopup = true;
      },
      // 关闭规格选择弹窗
      closeSpecPopup() {
        this.showPopup = false;
      },
      // 直接购买：不弹出弹窗，直接跳转结算
      buyNow() {
        if (this.product.has_specs && this.product.specs && this.product.specs.length > 0 && !this.selectedCombination) {
          uni.showToast({
            title: "请选择完整规格",
            icon: "error"
          });
          return;
        }
        if (this.quantity < 1 || this.quantity > this.currentStock) {
          uni.showToast({
            title: "请选择有效的购买数量",
            icon: "error"
          });
          return;
        }
        if (this.selectedAddress) {
          AddressService.setSelectedAddress(this.selectedAddress);
        }
        ({
          product_id: this.product.id,
          product_name: this.product.name,
          product_image: this.product.images && this.product.images[0] || "/static/default-product.png",
          price: this.currentPrice,
          quantity: this.quantity,
          spec_combination_id: this.selectedCombination ? this.selectedCombination.id : null,
          spec_combination_name: this.selectedCombination ? this.selectedCombination.name : null,
          subtotal: this.currentPrice * this.quantity
        });
        uni.navigateTo({
          url: "/pages/checkout/checkout?product_id=" + this.product.id + "&quantity=" + this.quantity + "&spec_combination_id=" + this.selectedCombination
        });
      },
      // 选择规格
      selectSpec(name, value) {
        if (this.isSpecDisabled(name, value)) {
          return;
        }
        this.$set(this.selectedSpecs, name, value);
        this.updateSelectedSpecText();
        this.findMatchingCombination();
      },
      // 检查规格是否已选择
      isSpecSelected(name, value) {
        return this.selectedSpecs[name] === value;
      },
      // 检查规格是否禁用
      isSpecDisabled(name, value) {
        if (!this.product.spec_combinations || this.product.spec_combinations.length === 0) {
          return false;
        }
        const currentSpecs = {
          ...this.selectedSpecs
        };
        currentSpecs[name] = value;
        const hasMatchingCombination = this.product.spec_combinations.some((combo) => {
          return this.isSpecCombinationMatch(combo.spec_values, currentSpecs);
        });
        return !hasMatchingCombination;
      },
      // 检查规格组合是否匹配
      isSpecCombinationMatch(comboSpecs, selectedSpecs) {
        for (const specName in selectedSpecs) {
          if (comboSpecs[specName] !== selectedSpecs[specName]) {
            return false;
          }
        }
        return true;
      },
      // 更新已选规格文本
      updateSelectedSpecText() {
        const selected = [];
        for (const name in this.selectedSpecs) {
          selected.push(this.selectedSpecs[name]);
        }
        this.selectedSpec = selected.join(" ");
      },
      // 查找匹配的规格组合
      findMatchingCombination() {
        if (!this.product.spec_combinations || this.product.spec_combinations.length === 0) {
          this.selectedCombination = null;
          return;
        }
        if (Object.keys(this.selectedSpecs).length !== this.product.specs.length) {
          this.selectedCombination = null;
          return;
        }
        const matchingCombo = this.product.spec_combinations.find((combo) => {
          return this.isSpecCombinationMatch(combo.spec_values, this.selectedSpecs);
        });
        this.selectedCombination = matchingCombo || null;
      },
      // 增加数量
      increaseQuantity() {
        if (this.quantity < this.currentStock) {
          this.quantity++;
        } else {
          uni.showToast({
            title: "已达到最大库存",
            icon: "error"
          });
        }
      },
      // 减少数量
      decreaseQuantity() {
        if (this.quantity > 1) {
          this.quantity--;
        }
      },
      // 验证数量输入
      validateQuantity() {
        if (this.quantity < 1) {
          this.quantity = 1;
        } else if (this.quantity > this.currentStock) {
          this.quantity = this.currentStock;
        }
      },
      // 加入购物车
      async addToCart() {
        if (this.product.has_specs && this.product.specs && this.product.specs.length > 0 && Object.keys(this.selectedSpecs).length < this.product.specs.length) {
          this.showSpecPopup();
          return;
        }
        try {
          const cartData = {
            product_id: this.product.id,
            quantity: this.quantity,
            user_id: getUserId()
          };
          if (this.selectedCombination) {
            cartData.spec_combination_id = this.selectedCombination.id;
          }
          const response = await cartApi.addToCart(cartData);
          if (response.data.code === 200) {
            uni.showToast({
              title: "已加入购物车",
              icon: "success"
            });
            this.fetchCartCount();
          } else {
            uni.showToast({
              title: response.data.message || "加入购物车失败",
              icon: "error"
            });
          }
        } catch (error) {
          formatAppLog("error", "at pages/product-detail/product-detail.vue:715", "加入购物车失败:", error);
          uni.showToast({
            title: "网络错误，请重试",
            icon: "error"
          });
        }
      },
      // 跳转到客服页面
      goToCustomerService() {
        uni.switchTab({
          url: "/pages/customer-service/customer-service"
        });
      },
      // 跳转到店铺页面
      goToShop() {
        uni.switchTab({
          url: "/pages/shop/shop"
        });
      },
      // 跳转到购物车页面
      goToCart() {
        uni.switchTab({
          url: "/pages/cart/cart"
        });
      },
      // 确认规格选择
      confirmSpec() {
        if (this.product.has_specs && this.product.specs && this.product.specs.length > 0 && Object.keys(this.selectedSpecs).length < this.product.specs.length) {
          uni.showToast({
            title: "请选择完整规格",
            icon: "error"
          });
          return;
        }
        if (this.product.has_specs && !this.selectedCombination) {
          uni.showToast({
            title: "所选规格组合不可用",
            icon: "error"
          });
          return;
        }
        if (this.quantity < 1 || this.quantity > this.currentStock) {
          uni.showToast({
            title: "请选择有效的购买数量",
            icon: "error"
          });
          return;
        }
        this.closeSpecPopup();
        this.navigateToPayment();
      },
      // 跳转到下单页面
      navigateToPayment() {
        const params = {
          product_id: this.product.id,
          quantity: this.quantity
        };
        if (this.selectedCombination) {
          params.spec_combination_id = this.selectedCombination.id;
        }
        const queryString = Object.keys(params).map((key) => `${key}=${encodeURIComponent(params[key])}`).join("&");
        uni.navigateTo({
          url: `/pages/checkout/checkout?${queryString}`
        });
      },
      // 选择收货地址
      selectAddress() {
        uni.navigateTo({
          url: "/pages/address/address?from=product-detail"
        });
      },
      // 确认立即购买
      confirmDirectBuy() {
        if (!this.selectedAddress) {
          uni.showToast({
            title: "请先选择收货地址",
            icon: "error"
          });
          return;
        }
        if (this.product.has_specs && this.product.specs && this.product.specs.length > 0 && Object.keys(this.selectedSpecs).length < this.product.specs.length) {
          uni.showToast({
            title: "请选择完整规格",
            icon: "error"
          });
          return;
        }
        if (!this.selectedCombination) {
          uni.showToast({
            title: "所选规格组合不可用",
            icon: "error"
          });
          return;
        }
        if (this.quantity < 1 || this.quantity > this.currentStock) {
          uni.showToast({
            title: "请选择有效的购买数量",
            icon: "error"
          });
          return;
        }
        AddressService.setSelectedAddress(this.selectedAddress);
        this.closeSpecPopup();
        uni.navigateTo({
          url: "/pages/checkout/checkout?product_id=" + this.product.id + "&quantity=" + this.quantity + "&spec_combination_id=" + this.selectedCombination ? this.selectedCombination.id : null
        });
      }
    }
  };
  function _sfc_render$c(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "product-detail-container" }, [
      vue.createCommentVNode(" 顶部导航栏 "),
      vue.createElementVNode("view", { class: "nav-bar" }, [
        vue.createElementVNode("view", {
          class: "nav-left",
          onClick: _cache[0] || (_cache[0] = (...args) => $options.goBack && $options.goBack(...args))
        }, [
          vue.createElementVNode("text", { class: "nav-icon" }, "‹")
        ]),
        vue.createElementVNode("view", { class: "nav-tabs" }, [
          (vue.openBlock(true), vue.createElementBlock(
            vue.Fragment,
            null,
            vue.renderList($data.tabs, (tab, index) => {
              return vue.openBlock(), vue.createElementBlock("view", {
                key: index,
                class: vue.normalizeClass(["tab-item", { active: $data.currentTab === index }]),
                onClick: ($event) => $options.switchTab(index)
              }, vue.toDisplayString(tab), 11, ["onClick"]);
            }),
            128
            /* KEYED_FRAGMENT */
          ))
        ]),
        vue.createElementVNode("view", { class: "nav-right" }, [
          vue.createElementVNode("text", {
            class: "nav-icon",
            onClick: _cache[1] || (_cache[1] = (...args) => $options.shareProduct && $options.shareProduct(...args))
          }, "��")
        ])
      ]),
      vue.createCommentVNode(" 商品轮播图 "),
      vue.createElementVNode("view", { class: "product-swiper" }, [
        vue.createElementVNode("view", { class: "swiper-container" }, [
          vue.createElementVNode(
            "view",
            {
              class: "swiper-wrapper",
              style: vue.normalizeStyle({ transform: `translateX(-${$data.currentImageIndex * 100}%)` })
            },
            [
              (vue.openBlock(true), vue.createElementBlock(
                vue.Fragment,
                null,
                vue.renderList($options.productImages, (image, index) => {
                  return vue.openBlock(), vue.createElementBlock("view", {
                    key: index,
                    class: "swiper-slide"
                  }, [
                    vue.createElementVNode("image", {
                      class: "swiper-image",
                      src: image,
                      onClick: ($event) => $options.previewImage(index)
                    }, null, 8, ["src", "onClick"])
                  ]);
                }),
                128
                /* KEYED_FRAGMENT */
              ))
            ],
            4
            /* STYLE */
          ),
          $options.productImages.length > 1 ? (vue.openBlock(), vue.createElementBlock("view", {
            key: 0,
            class: "swiper-pagination"
          }, [
            (vue.openBlock(true), vue.createElementBlock(
              vue.Fragment,
              null,
              vue.renderList($options.productImages, (image, index) => {
                return vue.openBlock(), vue.createElementBlock("text", {
                  key: index,
                  class: vue.normalizeClass(["pagination-dot", { active: $data.currentImageIndex === index }]),
                  onClick: ($event) => $options.goToImage(index)
                }, null, 10, ["onClick"]);
              }),
              128
              /* KEYED_FRAGMENT */
            ))
          ])) : vue.createCommentVNode("v-if", true),
          $options.productImages.length > 1 ? (vue.openBlock(), vue.createElementBlock("view", {
            key: 1,
            class: "swiper-nav"
          }, [
            vue.createElementVNode("button", {
              class: "swiper-btn swiper-prev",
              onClick: _cache[2] || (_cache[2] = (...args) => $options.prevImage && $options.prevImage(...args))
            }, "‹"),
            vue.createElementVNode("button", {
              class: "swiper-btn swiper-next",
              onClick: _cache[3] || (_cache[3] = (...args) => $options.nextImage && $options.nextImage(...args))
            }, "›")
          ])) : vue.createCommentVNode("v-if", true)
        ])
      ]),
      vue.createCommentVNode(" 商品基本信息 "),
      vue.createElementVNode("view", { class: "product-info" }, [
        vue.createElementVNode("view", { class: "price-section" }, [
          vue.createElementVNode(
            "text",
            { class: "current-price" },
            "¥" + vue.toDisplayString($options.currentPrice),
            1
            /* TEXT */
          ),
          $data.product.original_price && $data.product.original_price > $options.currentPrice ? (vue.openBlock(), vue.createElementBlock(
            "text",
            {
              key: 0,
              class: "original-price"
            },
            " ¥" + vue.toDisplayString($data.product.original_price),
            1
            /* TEXT */
          )) : vue.createCommentVNode("v-if", true),
          $data.product.original_price && $data.product.original_price > $options.currentPrice ? (vue.openBlock(), vue.createElementBlock(
            "text",
            {
              key: 1,
              class: "discount-tag"
            },
            " 省¥" + vue.toDisplayString(($data.product.original_price - $options.currentPrice).toFixed(2)),
            1
            /* TEXT */
          )) : vue.createCommentVNode("v-if", true)
        ]),
        vue.createElementVNode("view", { class: "title-section" }, [
          vue.createElementVNode(
            "h1",
            { class: "product-title" },
            vue.toDisplayString($data.product.name),
            1
            /* TEXT */
          ),
          vue.createElementVNode(
            "p",
            { class: "product-subtitle" },
            vue.toDisplayString($data.product.description),
            1
            /* TEXT */
          )
        ])
      ]),
      vue.createCommentVNode(" 商品规格信息 "),
      $data.product.has_specs && $data.product.specs ? (vue.openBlock(), vue.createElementBlock("view", {
        key: 0,
        class: "spec-info"
      }, [
        vue.createElementVNode("view", {
          class: "spec-preview single-line",
          onClick: _cache[4] || (_cache[4] = (...args) => $options.showSpecPopup && $options.showSpecPopup(...args))
        }, [
          vue.createElementVNode("text", { class: "spec-label" }, "规格"),
          vue.createElementVNode(
            "text",
            { class: "spec-value-line" },
            vue.toDisplayString($options.selectedSpecText || "请选择规格"),
            1
            /* TEXT */
          ),
          vue.createElementVNode(
            "text",
            { class: "spec-qty" },
            "数量 " + vue.toDisplayString($data.quantity) + " 件",
            1
            /* TEXT */
          ),
          vue.createElementVNode("text", { class: "spec-arrow" }, [
            vue.createElementVNode("text", { class: "arrow-icon" }, "›")
          ])
        ])
      ])) : vue.createCommentVNode("v-if", true),
      vue.createCommentVNode(" 收货地址预览 "),
      vue.createElementVNode("view", {
        class: "address-preview",
        onClick: _cache[5] || (_cache[5] = (...args) => $options.selectAddress && $options.selectAddress(...args))
      }, [
        vue.createElementVNode("view", { class: "address-preview-title" }, "收货地址"),
        $data.selectedAddress ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 0,
          class: "address-preview-content"
        }, [
          vue.createElementVNode("view", { class: "address-preview-text" }, [
            vue.createElementVNode(
              "view",
              { class: "address-line" },
              vue.toDisplayString($data.selectedAddress.full_address),
              1
              /* TEXT */
            ),
            vue.createElementVNode("view", { class: "address-estimate" }, "预计3-5日送达")
          ]),
          vue.createElementVNode("view", { class: "address-preview-arrow" }, "›")
        ])) : (vue.openBlock(), vue.createElementBlock("view", {
          key: 1,
          class: "address-preview-empty"
        }, [
          vue.createElementVNode("text", null, "请选择收货地址"),
          vue.createElementVNode("view", { class: "address-preview-arrow" }, "›")
        ]))
      ]),
      vue.createCommentVNode(" 服务保障独立一行 "),
      vue.createElementVNode("view", { class: "service-guarantee" }, [
        vue.createElementVNode("text", { class: "guarantee-icon" }, "✓"),
        vue.createElementVNode("text", { class: "guarantee-text" }, "正品保证 · 7天无理由退换")
      ]),
      vue.createCommentVNode(" 商品评价 "),
      vue.createElementVNode("view", { class: "review-section" }, [
        vue.createElementVNode("view", { class: "section-header" }, [
          vue.createElementVNode(
            "h3",
            { class: "section-title" },
            "商品评价(" + vue.toDisplayString($data.product.review_count || 0) + ")",
            1
            /* TEXT */
          ),
          vue.createElementVNode(
            "text",
            {
              class: "more-link",
              onClick: _cache[6] || (_cache[6] = (...args) => $options.goToReviews && $options.goToReviews(...args))
            },
            "好评率" + vue.toDisplayString($data.product.positive_rate || 98) + "% ›",
            1
            /* TEXT */
          )
        ]),
        $data.product.top_review ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 0,
          class: "review-item"
        }, [
          vue.createElementVNode("view", { class: "user-info" }, [
            vue.createElementVNode("image", {
              class: "user-avatar",
              src: $data.product.top_review.user.avatar
            }, null, 8, ["src"]),
            vue.createElementVNode(
              "text",
              { class: "user-name" },
              vue.toDisplayString($data.product.top_review.user.name),
              1
              /* TEXT */
            )
          ]),
          vue.createElementVNode("view", { class: "review-content" }, [
            vue.createElementVNode(
              "p",
              null,
              vue.toDisplayString($data.product.top_review.content),
              1
              /* TEXT */
            )
          ]),
          $data.product.top_review.images && $data.product.top_review.images.length > 0 ? (vue.openBlock(), vue.createElementBlock("view", {
            key: 0,
            class: "review-images"
          }, [
            (vue.openBlock(true), vue.createElementBlock(
              vue.Fragment,
              null,
              vue.renderList($data.product.top_review.images, (img, index) => {
                return vue.openBlock(), vue.createElementBlock("image", {
                  key: index,
                  src: img,
                  class: "review-image",
                  onClick: ($event) => $options.previewReviewImage(index)
                }, null, 8, ["src", "onClick"]);
              }),
              128
              /* KEYED_FRAGMENT */
            ))
          ])) : vue.createCommentVNode("v-if", true),
          vue.createElementVNode("view", { class: "review-spec" }, [
            vue.createElementVNode(
              "text",
              null,
              vue.toDisplayString($data.product.top_review.spec),
              1
              /* TEXT */
            ),
            vue.createElementVNode(
              "text",
              { class: "review-time" },
              vue.toDisplayString($data.product.top_review.time),
              1
              /* TEXT */
            )
          ])
        ])) : vue.createCommentVNode("v-if", true)
      ]),
      vue.createCommentVNode(" 商品详情 "),
      vue.createElementVNode("view", { class: "detail-section" }, [
        vue.createElementVNode("view", { class: "section-header" }, [
          vue.createElementVNode("h3", { class: "section-title" }, "商品详情")
        ]),
        vue.createElementVNode("view", {
          class: "detail-content",
          innerHTML: $data.product.detail || "<p style='color: #999; text-align: center; padding: 20px;'>暂无详情</p>"
        }, null, 8, ["innerHTML"])
      ]),
      vue.createCommentVNode(" 底部操作栏 "),
      !$data.showPopup ? (vue.openBlock(), vue.createElementBlock("view", {
        key: 1,
        class: "bottom-bar"
      }, [
        vue.createElementVNode("view", { class: "action-btn" }, [
          vue.createElementVNode("view", {
            class: "btn-icon",
            onClick: _cache[7] || (_cache[7] = (...args) => $options.goToCustomerService && $options.goToCustomerService(...args))
          }, [
            vue.createElementVNode("text", { class: "btn-text" }, "客服")
          ]),
          vue.createElementVNode("view", {
            class: "btn-icon",
            onClick: _cache[8] || (_cache[8] = (...args) => $options.goToShop && $options.goToShop(...args))
          }, [
            vue.createElementVNode("text", { class: "btn-text" }, "进店")
          ]),
          vue.createElementVNode("view", {
            class: "btn-icon",
            onClick: _cache[9] || (_cache[9] = (...args) => $options.goToCart && $options.goToCart(...args))
          }, [
            vue.createElementVNode("text", { class: "btn-text" }, "购物车"),
            $data.cartCount > 0 ? (vue.openBlock(), vue.createElementBlock(
              "text",
              {
                key: 0,
                class: "cart-badge"
              },
              vue.toDisplayString($data.cartCount),
              1
              /* TEXT */
            )) : vue.createCommentVNode("v-if", true)
          ])
        ]),
        vue.createElementVNode("view", { class: "main-btn" }, [
          vue.createElementVNode("view", {
            class: "add-cart-btn",
            onClick: _cache[10] || (_cache[10] = (...args) => $options.addToCart && $options.addToCart(...args))
          }, "加入购物车"),
          vue.createElementVNode("view", {
            class: "buy-now-btn",
            onClick: _cache[11] || (_cache[11] = (...args) => $options.buyNow && $options.buyNow(...args))
          }, "立即购买")
        ])
      ])) : vue.createCommentVNode("v-if", true),
      vue.createCommentVNode(" 规格选择弹出层 "),
      $data.showPopup ? (vue.openBlock(), vue.createElementBlock("view", {
        key: 2,
        class: "spec-popup-overlay",
        onClick: _cache[19] || (_cache[19] = (...args) => $options.closeSpecPopup && $options.closeSpecPopup(...args))
      }, [
        vue.createElementVNode("view", {
          class: "spec-popup",
          onClick: _cache[18] || (_cache[18] = vue.withModifiers(() => {
          }, ["stop"]))
        }, [
          vue.createElementVNode("view", { class: "popup-header" }, [
            vue.createElementVNode("view", { class: "product-basic-info" }, [
              vue.createElementVNode("image", {
                class: "product-image",
                src: $options.currentImage,
                alt: "商品图片"
              }, null, 8, ["src"]),
              vue.createElementVNode("view", { class: "product-info" }, [
                vue.createElementVNode(
                  "view",
                  { class: "product-title" },
                  vue.toDisplayString($data.product.name),
                  1
                  /* TEXT */
                ),
                vue.createElementVNode("view", { class: "price-info" }, [
                  vue.createElementVNode(
                    "text",
                    { class: "current-price" },
                    "¥" + vue.toDisplayString($options.currentPrice),
                    1
                    /* TEXT */
                  ),
                  $data.product.original_price && $data.product.original_price > $options.currentPrice ? (vue.openBlock(), vue.createElementBlock(
                    "text",
                    {
                      key: 0,
                      class: "original-price"
                    },
                    " ¥" + vue.toDisplayString($data.product.original_price),
                    1
                    /* TEXT */
                  )) : vue.createCommentVNode("v-if", true)
                ])
              ])
            ]),
            vue.createElementVNode("text", {
              class: "close-btn",
              onClick: _cache[12] || (_cache[12] = (...args) => $options.closeSpecPopup && $options.closeSpecPopup(...args))
            }, "×")
          ]),
          vue.createElementVNode("view", { class: "spec-content" }, [
            vue.createCommentVNode(" 规格选择 "),
            $data.product.has_specs && $data.product.specs && $data.product.specs.length > 0 ? (vue.openBlock(), vue.createElementBlock("view", {
              key: 0,
              class: "spec-section"
            }, [
              vue.createElementVNode("view", { class: "section-title" }, [
                vue.createElementVNode("text", { class: "title-text" }, "选择规格"),
                !$options.canConfirm ? (vue.openBlock(), vue.createElementBlock("text", {
                  key: 0,
                  class: "title-tip"
                }, "请选择完整规格")) : vue.createCommentVNode("v-if", true)
              ]),
              vue.createElementVNode("view", { class: "spec-groups" }, [
                (vue.openBlock(true), vue.createElementBlock(
                  vue.Fragment,
                  null,
                  vue.renderList($data.product.specs, (group, index) => {
                    return vue.openBlock(), vue.createElementBlock("view", {
                      class: "spec-group",
                      key: index
                    }, [
                      vue.createElementVNode("view", { class: "spec-group-header" }, [
                        vue.createElementVNode(
                          "text",
                          { class: "spec-name" },
                          vue.toDisplayString(group.name),
                          1
                          /* TEXT */
                        ),
                        vue.createElementVNode("text", { class: "spec-required" }, "*")
                      ]),
                      vue.createElementVNode("view", { class: "spec-values" }, [
                        (vue.openBlock(true), vue.createElementBlock(
                          vue.Fragment,
                          null,
                          vue.renderList(group.values, (value, vIndex) => {
                            return vue.openBlock(), vue.createElementBlock("text", {
                              key: vIndex,
                              class: vue.normalizeClass(["spec-value-item", {
                                selected: $options.isSpecSelected(group.name, value),
                                disabled: $options.isSpecDisabled(group.name, value)
                              }]),
                              onClick: ($event) => $options.selectSpec(group.name, value)
                            }, [
                              vue.createElementVNode(
                                "text",
                                { class: "value-text" },
                                vue.toDisplayString(value),
                                1
                                /* TEXT */
                              ),
                              $options.isSpecSelected(group.name, value) ? (vue.openBlock(), vue.createElementBlock("text", {
                                key: 0,
                                class: "value-check"
                              }, "✓")) : vue.createCommentVNode("v-if", true)
                            ], 10, ["onClick"]);
                          }),
                          128
                          /* KEYED_FRAGMENT */
                        ))
                      ])
                    ]);
                  }),
                  128
                  /* KEYED_FRAGMENT */
                ))
              ]),
              $data.selectedSpec ? (vue.openBlock(), vue.createElementBlock("view", {
                key: 0,
                class: "selected-spec-display"
              }, [
                vue.createElementVNode("view", { class: "selected-header" }, [
                  vue.createElementVNode("text", { class: "selected-label" }, "已选规格"),
                  $data.selectedCombination ? (vue.openBlock(), vue.createElementBlock(
                    "text",
                    {
                      key: 0,
                      class: "selected-price"
                    },
                    "¥" + vue.toDisplayString($data.selectedCombination.price),
                    1
                    /* TEXT */
                  )) : vue.createCommentVNode("v-if", true)
                ]),
                vue.createElementVNode(
                  "view",
                  { class: "selected-text" },
                  vue.toDisplayString($data.selectedSpec),
                  1
                  /* TEXT */
                )
              ])) : vue.createCommentVNode("v-if", true)
            ])) : vue.createCommentVNode("v-if", true),
            vue.createCommentVNode(" 数量选择 "),
            vue.createElementVNode("view", { class: "quantity-section" }, [
              vue.createElementVNode("view", { class: "section-title" }, [
                vue.createElementVNode("text", { class: "title-text" }, "购买数量")
              ]),
              vue.createElementVNode("view", { class: "quantity-selector" }, [
                vue.createElementVNode("button", {
                  class: vue.normalizeClass(["quantity-btn minus-btn", { disabled: $data.quantity <= 1 }]),
                  onClick: _cache[13] || (_cache[13] = (...args) => $options.decreaseQuantity && $options.decreaseQuantity(...args)),
                  disabled: $data.quantity <= 1
                }, [
                  vue.createElementVNode("text", { class: "btn-icon" }, "-")
                ], 10, ["disabled"]),
                vue.createElementVNode("view", { class: "quantity-input-wrapper" }, [
                  vue.withDirectives(vue.createElementVNode("input", {
                    class: "quantity-input",
                    type: "number",
                    "onUpdate:modelValue": _cache[14] || (_cache[14] = ($event) => $data.quantity = $event),
                    min: "1",
                    max: $options.currentStock,
                    onInput: _cache[15] || (_cache[15] = (...args) => $options.validateQuantity && $options.validateQuantity(...args))
                  }, null, 40, ["max"]), [
                    [
                      vue.vModelText,
                      $data.quantity,
                      void 0,
                      { number: true }
                    ]
                  ])
                ]),
                vue.createElementVNode("button", {
                  class: vue.normalizeClass(["quantity-btn plus-btn", { disabled: $data.quantity >= $options.currentStock }]),
                  onClick: _cache[16] || (_cache[16] = (...args) => $options.increaseQuantity && $options.increaseQuantity(...args)),
                  disabled: $data.quantity >= $options.currentStock
                }, [
                  vue.createElementVNode("text", { class: "btn-icon" }, "+")
                ], 10, ["disabled"])
              ])
            ])
          ]),
          vue.createCommentVNode(" 底部确认区域 "),
          vue.createElementVNode("view", { class: "popup-footer" }, [
            vue.createElementVNode("view", { class: "total-info" }, [
              vue.createElementVNode("text", { class: "total-label" }, "合计："),
              vue.createElementVNode(
                "text",
                { class: "total-price" },
                "¥" + vue.toDisplayString(($options.currentPrice * $data.quantity).toFixed(2)),
                1
                /* TEXT */
              )
            ]),
            vue.createElementVNode(
              "view",
              {
                class: vue.normalizeClass(["confirm-btn", { disabled: !$options.canConfirm || !$data.selectedAddress }]),
                onClick: _cache[17] || (_cache[17] = (...args) => $options.confirmDirectBuy && $options.confirmDirectBuy(...args))
              },
              " 立即购买 ",
              2
              /* CLASS */
            )
          ])
        ])
      ])) : vue.createCommentVNode("v-if", true)
    ]);
  }
  const PagesProductDetailProductDetail = /* @__PURE__ */ _export_sfc(_sfc_main$d, [["render", _sfc_render$c], ["__scopeId", "data-v-4d4a2bad"], ["__file", "/Users/chenjianping/Desktop/private/pro/sheng/yinjiajia/app/front-app-uni/pages/product-detail/product-detail.vue"]]);
  const _sfc_main$c = {
    name: "Checkout",
    data() {
      return {
        user_id: getUserId(),
        selectedAddress: null,
        products: [],
        totalAmount: 0,
        cartItemIds: [],
        directBuyProduct: null,
        selectedMethod: "wechat",
        // 模拟三方支付
        showPaymentModal: false,
        isProcessing: false,
        currentOrderNumbers: [],
        currentTotalAmount: 0,
        // 页面参数
        pageParams: {},
        // 优惠信息
        discountAmount: 0
      };
    },
    computed: {
      // 计算商品总数量
      totalQuantity() {
        const total = this.products.reduce((total2, product) => total2 + (product.quantity || 0), 0);
        return total;
      },
      // 计算最终实付金额
      finalAmount() {
        const final = Math.max(0, this.totalAmount - this.discountAmount);
        return final;
      }
    },
    onLoad(options) {
      this.pageParams = options;
      this.loadCheckoutInfo();
    },
    onShow() {
      this.loadAddressInfo();
      const cached = AddressService.getSelectedAddress();
      if (cached) {
        this.selectedAddress = cached;
      }
    },
    methods: {
      orderNumbersPreview() {
        if (!this.currentOrderNumbers || this.currentOrderNumbers.length <= 1)
          return "";
        const list = this.currentOrderNumbers.slice(0, 2);
        const more = this.currentOrderNumbers.length - list.length;
        return `${list.join(", ")}${more > 0 ? ` 等${this.currentOrderNumbers.length}单` : ""}`;
      },
      formatPrice(value) {
        const num = Number(value || 0);
        return num.toFixed(2);
      },
      goBack() {
        uni.navigateBack();
      },
      async loadCheckoutInfo() {
        try {
          const { cart_items, product_id, quantity, spec_combination_id } = this.pageParams;
          formatAppLog("log", "at pages/checkout/checkout.vue:258", " ------ >>>>>>>   ", product_id, quantity, spec_combination_id);
          let params = {
            user_id: this.user_id
          };
          if (cart_items) {
            params.cart_items = cart_items;
          }
          if (product_id) {
            params.product_id = product_id;
            params.quantity = quantity || 1;
            if (spec_combination_id) {
              params.spec_combination_id = spec_combination_id;
            }
          }
          const { address_id } = this.pageParams;
          if (address_id) {
            params.address_id = address_id;
          }
          try {
            const checkoutResponse = await request$1.get("/api/app/order/checkout", params);
            if (checkoutResponse.data.code === 200) {
              const data = checkoutResponse.data.data;
              this.products = data.products || [];
              this.totalAmount = data.total_amount || 0;
            }
          } catch (checkoutError) {
            formatAppLog("error", "at pages/checkout/checkout.vue:291", "从checkout API加载失败:", checkoutError);
            if (cart_items) {
              try {
                const cartResponse = await request$1.get("/api/app/cart/", {
                  params: {
                    user_id: this.user_id
                  }
                });
                if (cartResponse.data.code === 200) {
                  const cartData = cartResponse.data.data;
                  if (cartData && cartData.items) {
                    const cartItemIds = cart_items.split(",").map((id) => parseInt(id));
                    const selectedItems = cartData.items.filter(
                      (item) => cartItemIds.includes(item.id)
                    );
                    this.products = selectedItems.map((item) => ({
                      product_id: item.product_id,
                      product_name: item.product_name,
                      product_image: item.product_image,
                      price: item.price,
                      quantity: item.quantity,
                      spec_combination_id: item.spec_combination_id,
                      spec_combination_name: item.spec_combination_name,
                      item_total: item.item_total
                    }));
                    this.totalAmount = this.products.reduce((total, item) => {
                      return total + (item.item_total || 0);
                    }, 0);
                  }
                }
              } catch (cartError) {
                formatAppLog("error", "at pages/checkout/checkout.vue:329", "从购物车加载商品失败:", cartError);
              }
            }
          }
          await this.loadAddressInfo();
        } catch (error) {
          formatAppLog("error", "at pages/checkout/checkout.vue:337", "加载下单信息失败:", error);
          uni.showToast({
            title: "加载商品信息失败，请重试",
            icon: "none"
          });
        }
      },
      selectAddress() {
        uni.navigateTo({
          url: "/pages/address-list/address-list?from=checkout"
        });
      },
      async loadAddressInfo() {
        try {
          const { address_id } = this.pageParams;
          if (address_id) {
            const cached = AddressService.getSelectedAddress();
            if (cached && String(cached.id) === String(address_id)) {
              this.selectedAddress = cached;
              return;
            } else {
              try {
              } catch (error) {
                formatAppLog("error", "at pages/checkout/checkout.vue:374", "加载地址详情失败:", error);
              }
            }
          }
          this.selectedAddress = await AddressService.getDefaultAddress(this.user_id);
        } catch (error) {
          formatAppLog("error", "at pages/checkout/checkout.vue:382", "加载地址信息失败:", error);
        }
      },
      // 去结算：创建订单 -> 弹窗模拟支付
      async handleCheckout() {
        if (!this.selectedAddress) {
          uni.showToast({
            title: "请选择收货地址",
            icon: "none"
          });
          return;
        }
        try {
          const orderData = {
            user_id: this.user_id,
            address_id: this.selectedAddress.id,
            payment_method: this.selectedMethod
          };
          const { cart_items, product_id, quantity, spec_combination_id } = this.pageParams;
          if (cart_items) {
            orderData.cart_items = cart_items.split(",").map((id) => parseInt(id));
          } else if (product_id) {
            orderData.direct_buy = {
              product_id: parseInt(product_id),
              quantity: parseInt(quantity) || 1
            };
            if (spec_combination_id) {
              orderData.direct_buy.spec_combination_id = parseInt(spec_combination_id);
            }
          }
          const res = await request$1.post("/api/app/order/", orderData);
          if (res.data.code !== 200) {
            throw new Error(res.data.message || "下单失败");
          }
          const payload = res.data.data;
          if (payload.orders && Array.isArray(payload.orders)) {
            this.currentOrderNumbers = payload.orders.map((o) => o.order_number);
            this.currentTotalAmount = payload.total_amount || payload.orders.reduce((s, o) => s + Number(o.total_amount || 0), 0);
          } else {
            this.currentOrderNumbers = [payload.order_number];
            this.currentTotalAmount = payload.total_amount;
          }
          this.currentTotalAmount = this.finalAmount;
          this.showPaymentModal = true;
        } catch (error) {
          formatAppLog("error", "at pages/checkout/checkout.vue:435", "去结算失败:", error);
          uni.showToast({
            title: "去结算失败：" + (error.message || "请稍后重试"),
            icon: "none"
          });
        }
      },
      cancelPayment() {
        if (this.isProcessing)
          return;
        this.showPaymentModal = false;
      },
      async processPayment() {
        if (this.isProcessing)
          return;
        if (!this.currentOrderNumbers || this.currentOrderNumbers.length === 0)
          return;
        this.isProcessing = true;
        try {
          for (const on of this.currentOrderNumbers) {
            const payRes = await request$1.post(`/api/app/order/${on}/pay-success`, {
              user_id: this.user_id,
              payment_method: this.selectedMethod
            });
            if (payRes.data.code !== 200) {
              throw new Error(payRes.data.message || "支付失败");
            }
          }
          {
            this.showPaymentModal = false;
            uni.navigateTo({
              url: `/pages/pay-result/pay-result?status=success&order_number=${this.currentOrderNumbers.join(",")}&total_amount=${this.currentTotalAmount}`
            });
          }
        } catch (err) {
          formatAppLog("error", "at pages/checkout/checkout.vue:471", "支付失败:", err);
          uni.showToast({
            title: "支付失败：" + (err.message || "请稍后重试"),
            icon: "none"
          });
        } finally {
          this.isProcessing = false;
        }
      },
      handleImageError(e) {
        formatAppLog("error", "at pages/checkout/checkout.vue:482", "商品图片加载失败:", e.detail.message);
        e.target.src = "/static/default-product.png";
      }
    }
  };
  function _sfc_render$b(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "checkout-container" }, [
      vue.createCommentVNode(" 头部 "),
      vue.createElementVNode("view", { class: "header" }, [
        vue.createElementVNode("view", {
          class: "back-btn",
          onClick: _cache[0] || (_cache[0] = (...args) => $options.goBack && $options.goBack(...args))
        }, [
          vue.createElementVNode("text", null, "←")
        ]),
        vue.createElementVNode("view", { class: "title" }, "确认订单")
      ]),
      vue.createCommentVNode(" 收货地址 "),
      vue.createElementVNode("view", {
        class: "address-section",
        onClick: _cache[1] || (_cache[1] = (...args) => $options.selectAddress && $options.selectAddress(...args))
      }, [
        vue.createElementVNode("view", { class: "section-title" }, "收货地址"),
        $data.selectedAddress ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 0,
          class: "address-content"
        }, [
          vue.createElementVNode("view", { class: "address-info" }, [
            vue.createElementVNode("view", { class: "receiver-info" }, [
              vue.createElementVNode(
                "text",
                { class: "receiver-name" },
                vue.toDisplayString($data.selectedAddress.receiver_name),
                1
                /* TEXT */
              ),
              vue.createElementVNode(
                "text",
                { class: "receiver-phone" },
                vue.toDisplayString($data.selectedAddress.phone),
                1
                /* TEXT */
              )
            ]),
            vue.createElementVNode(
              "view",
              { class: "address-detail" },
              vue.toDisplayString($data.selectedAddress.full_address),
              1
              /* TEXT */
            )
          ]),
          vue.createElementVNode("view", { class: "address-arrow" }, "›")
        ])) : (vue.openBlock(), vue.createElementBlock("view", {
          key: 1,
          class: "no-address"
        }, [
          vue.createElementVNode("text", null, "请选择收货地址"),
          vue.createElementVNode("view", { class: "address-arrow" }, "›")
        ]))
      ]),
      vue.createCommentVNode(" 商品信息 "),
      vue.createElementVNode("view", { class: "products-section" }, [
        vue.createElementVNode("view", { class: "section-title" }, "商品信息"),
        $data.products.length > 0 ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 0,
          class: "product-list"
        }, [
          (vue.openBlock(true), vue.createElementBlock(
            vue.Fragment,
            null,
            vue.renderList($data.products, (product) => {
              return vue.openBlock(), vue.createElementBlock("view", {
                class: "product-item",
                key: product.product_id
              }, [
                vue.createElementVNode("view", { class: "product-image" }, [
                  vue.createElementVNode("image", {
                    src: product.product_image || "/static/default-product.png",
                    onError: _cache[2] || (_cache[2] = (...args) => $options.handleImageError && $options.handleImageError(...args)),
                    mode: "aspectFill"
                  }, null, 40, ["src"])
                ]),
                vue.createElementVNode("view", { class: "product-info" }, [
                  vue.createElementVNode(
                    "view",
                    { class: "product-name" },
                    vue.toDisplayString(product.product_name),
                    1
                    /* TEXT */
                  ),
                  product.spec_combination_id || product.spec_combination_name ? (vue.openBlock(), vue.createElementBlock("view", {
                    key: 0,
                    class: "product-specs"
                  }, [
                    vue.createElementVNode(
                      "text",
                      { class: "spec-text" },
                      vue.toDisplayString(product.spec_combination_name || `规格ID: ${product.spec_combination_id}`),
                      1
                      /* TEXT */
                    )
                  ])) : vue.createCommentVNode("v-if", true),
                  vue.createElementVNode(
                    "view",
                    { class: "product-price" },
                    "¥" + vue.toDisplayString($options.formatPrice(product.price)),
                    1
                    /* TEXT */
                  )
                ]),
                vue.createElementVNode("view", { class: "product-right" }, [
                  vue.createElementVNode(
                    "view",
                    { class: "product-quantity" },
                    "×" + vue.toDisplayString(product.quantity),
                    1
                    /* TEXT */
                  ),
                  vue.createElementVNode(
                    "view",
                    { class: "product-subtotal" },
                    "¥" + vue.toDisplayString($options.formatPrice(product.subtotal || product.price * product.quantity)),
                    1
                    /* TEXT */
                  )
                ])
              ]);
            }),
            128
            /* KEYED_FRAGMENT */
          ))
        ])) : (vue.openBlock(), vue.createElementBlock("view", {
          key: 1,
          class: "no-products"
        }, [
          vue.createElementVNode("text", null, "暂无商品信息")
        ]))
      ]),
      vue.createCommentVNode(" 订单信息 "),
      vue.createElementVNode("view", { class: "order-info-section" }, [
        vue.createElementVNode("view", { class: "section-title" }, "订单信息"),
        vue.createElementVNode("view", { class: "info-item" }, [
          vue.createElementVNode("text", { class: "label" }, "商品数量"),
          vue.createElementVNode(
            "text",
            { class: "value" },
            vue.toDisplayString($options.totalQuantity) + "件",
            1
            /* TEXT */
          )
        ]),
        vue.createElementVNode("view", { class: "info-item" }, [
          vue.createElementVNode("text", { class: "label" }, "商品总价"),
          vue.createElementVNode(
            "text",
            { class: "value" },
            "¥" + vue.toDisplayString($options.formatPrice($data.totalAmount)),
            1
            /* TEXT */
          )
        ]),
        vue.createElementVNode("view", { class: "info-item" }, [
          vue.createElementVNode("text", { class: "label" }, "运费"),
          vue.createElementVNode("text", { class: "value" }, "¥0.00")
        ]),
        $data.discountAmount > 0 ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 0,
          class: "info-item"
        }, [
          vue.createElementVNode("text", { class: "label" }, "优惠减免"),
          vue.createElementVNode(
            "text",
            { class: "value discount" },
            "-¥" + vue.toDisplayString($options.formatPrice($data.discountAmount)),
            1
            /* TEXT */
          )
        ])) : vue.createCommentVNode("v-if", true),
        vue.createElementVNode("view", { class: "info-item total" }, [
          vue.createElementVNode("text", { class: "label" }, "实付金额"),
          vue.createElementVNode(
            "text",
            { class: "value" },
            "¥" + vue.toDisplayString($options.formatPrice($options.finalAmount)),
            1
            /* TEXT */
          )
        ])
      ]),
      vue.createCommentVNode(" 支付方式 "),
      vue.createElementVNode("view", { class: "payment-method-section" }, [
        vue.createElementVNode("view", { class: "section-title" }, "选择支付方式"),
        vue.createElementVNode("view", { class: "payment-methods" }, [
          vue.createElementVNode(
            "view",
            {
              class: vue.normalizeClass(["payment-item", { selected: $data.selectedMethod === "alipay" }]),
              onClick: _cache[3] || (_cache[3] = ($event) => $data.selectedMethod = "alipay")
            },
            [
              vue.createElementVNode("view", { class: "method-left" }, [
                vue.createElementVNode("view", { class: "brand-badge alipay" }, [
                  vue.createElementVNode("text", { class: "brand-icon" }, "支")
                ]),
                vue.createElementVNode("view", { class: "method-info" }, [
                  vue.createElementVNode("text", { class: "method-name" }, "支付宝"),
                  vue.createElementVNode("text", { class: "method-desc" }, "推荐使用支付宝支付")
                ])
              ]),
              vue.createElementVNode("view", { class: "method-right" }, [
                vue.createElementVNode(
                  "view",
                  {
                    class: vue.normalizeClass(["checkmark", { active: $data.selectedMethod === "alipay" }])
                  },
                  null,
                  2
                  /* CLASS */
                )
              ])
            ],
            2
            /* CLASS */
          ),
          vue.createElementVNode(
            "view",
            {
              class: vue.normalizeClass(["payment-item", { selected: $data.selectedMethod === "wechat" }]),
              onClick: _cache[4] || (_cache[4] = ($event) => $data.selectedMethod = "wechat")
            },
            [
              vue.createElementVNode("view", { class: "method-left" }, [
                vue.createElementVNode("view", { class: "brand-badge wechat" }, [
                  vue.createElementVNode("text", { class: "brand-icon" }, "微")
                ]),
                vue.createElementVNode("view", { class: "method-info" }, [
                  vue.createElementVNode("text", { class: "method-name" }, "微信支付"),
                  vue.createElementVNode("text", { class: "method-desc" }, "使用微信扫码支付")
                ])
              ]),
              vue.createElementVNode("view", { class: "method-right" }, [
                vue.createElementVNode(
                  "view",
                  {
                    class: vue.normalizeClass(["checkmark", { active: $data.selectedMethod === "wechat" }])
                  },
                  null,
                  2
                  /* CLASS */
                )
              ])
            ],
            2
            /* CLASS */
          )
        ])
      ]),
      vue.createCommentVNode(" 底部提交按钮 "),
      vue.createElementVNode("view", { class: "bottom-bar" }, [
        vue.createElementVNode("view", { class: "total-info" }, [
          vue.createElementVNode("text", null, "合计："),
          vue.createElementVNode(
            "text",
            { class: "total-price" },
            "¥" + vue.toDisplayString($options.formatPrice($options.finalAmount)),
            1
            /* TEXT */
          )
        ]),
        vue.createElementVNode(
          "view",
          {
            class: vue.normalizeClass(["submit-btn", { disabled: !$data.selectedAddress }]),
            onClick: _cache[5] || (_cache[5] = (...args) => $options.handleCheckout && $options.handleCheckout(...args))
          },
          " 去结算 ",
          2
          /* CLASS */
        )
      ]),
      vue.createCommentVNode(" 支付确认弹窗（模拟三方支付） "),
      $data.showPaymentModal ? (vue.openBlock(), vue.createElementBlock("view", {
        key: 0,
        class: "payment-modal"
      }, [
        vue.createElementVNode("view", { class: "modal-content" }, [
          vue.createElementVNode("view", { class: "modal-header" }, [
            vue.createElementVNode("h3", null, "确认支付")
          ]),
          vue.createElementVNode("view", { class: "modal-body" }, [
            vue.createElementVNode("view", { class: "payment-detail" }, [
              vue.createElementVNode("view", { class: "detail-item" }, [
                vue.createElementVNode("text", { class: "label" }, "商品总价："),
                vue.createElementVNode(
                  "text",
                  { class: "value" },
                  "¥" + vue.toDisplayString($options.formatPrice($data.totalAmount)),
                  1
                  /* TEXT */
                )
              ]),
              $data.discountAmount > 0 ? (vue.openBlock(), vue.createElementBlock("view", {
                key: 0,
                class: "detail-item"
              }, [
                vue.createElementVNode("text", { class: "label" }, "优惠减免："),
                vue.createElementVNode(
                  "text",
                  { class: "value discount" },
                  "-¥" + vue.toDisplayString($options.formatPrice($data.discountAmount)),
                  1
                  /* TEXT */
                )
              ])) : vue.createCommentVNode("v-if", true),
              vue.createElementVNode("view", { class: "detail-item" }, [
                vue.createElementVNode("text", { class: "label" }, "运费："),
                vue.createElementVNode("text", { class: "value" }, "¥0.00")
              ]),
              vue.createElementVNode("view", { class: "detail-item total" }, [
                vue.createElementVNode("text", { class: "label" }, "实付金额："),
                vue.createElementVNode(
                  "text",
                  { class: "value" },
                  "¥" + vue.toDisplayString($options.formatPrice($data.currentTotalAmount)),
                  1
                  /* TEXT */
                )
              ])
            ]),
            vue.createElementVNode("view", { class: "payment-method-info" }, [
              vue.createElementVNode("text", { class: "label" }, "支付方式："),
              vue.createElementVNode(
                "text",
                { class: "value" },
                vue.toDisplayString($data.selectedMethod === "wechat" ? "微信支付" : "支付宝"),
                1
                /* TEXT */
              )
            ])
          ]),
          vue.createElementVNode("view", { class: "modal-footer" }, [
            vue.createElementVNode("button", {
              class: "cancel-btn",
              onClick: _cache[6] || (_cache[6] = (...args) => $options.cancelPayment && $options.cancelPayment(...args)),
              disabled: $data.isProcessing
            }, "取消", 8, ["disabled"]),
            vue.createElementVNode("button", {
              class: "confirm-btn",
              onClick: _cache[7] || (_cache[7] = (...args) => $options.processPayment && $options.processPayment(...args)),
              disabled: $data.isProcessing
            }, "确认支付", 8, ["disabled"])
          ])
        ])
      ])) : vue.createCommentVNode("v-if", true)
    ]);
  }
  const PagesCheckoutCheckout = /* @__PURE__ */ _export_sfc(_sfc_main$c, [["render", _sfc_render$b], ["__scopeId", "data-v-fd186f5c"], ["__file", "/Users/chenjianping/Desktop/private/pro/sheng/yinjiajia/app/front-app-uni/pages/checkout/checkout.vue"]]);
  const _sfc_main$b = {
    data() {
      return {
        orderInfo: {
          orderNo: "",
          createTime: "",
          productName: "",
          totalAmount: "0.00"
        },
        orderId: null,
        // 订单ID
        paymentMethods: [
          {
            name: "微信支付",
            value: "wechat",
            description: "推荐使用微信支付",
            icon: "wechat-icon"
          },
          {
            name: "支付宝",
            value: "alipay",
            description: "安全便捷的支付方式",
            icon: "alipay-icon"
          }
        ],
        currentMethod: "wechat",
        showPaymentModal: false,
        isProcessing: false
      };
    },
    mounted() {
      this.loadOrderInfo();
    },
    methods: {
      // 格式化日期
      formatDate(date) {
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, "0");
        const day = date.getDate().toString().padStart(2, "0");
        const hours = date.getHours().toString().padStart(2, "0");
        const minutes = date.getMinutes().toString().padStart(2, "0");
        const seconds = date.getSeconds().toString().padStart(2, "0");
        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
      },
      // 返回上一页
      goBack() {
        uni.navigateBack({
          delta: 1
        });
      },
      // 加载订单信息
      loadOrderInfo() {
        const pages = getCurrentPages();
        const currentPage = pages[pages.length - 1];
        const options = currentPage.options;
        this.orderInfo.orderNo = options.order_number || "";
        this.orderInfo.totalAmount = options.total_amount || "0.00";
        this.orderInfo.createTime = this.formatDate(/* @__PURE__ */ new Date());
        this.orderInfo.productName = "商品订单";
        this.currentMethod = options.payment_method || "wechat";
        this.orderId = options.order_id;
      },
      // 复制订单号
      copyOrderNo() {
        if (navigator.clipboard) {
          navigator.clipboard.writeText(this.orderInfo.orderNo).then(() => {
            alert("订单号已复制");
          }).catch(() => {
            alert("复制失败");
          });
        } else {
          const textArea = document.createElement("textarea");
          textArea.value = this.orderInfo.orderNo;
          document.body.appendChild(textArea);
          textArea.select();
          try {
            document.execCommand("copy");
            alert("订单号已复制");
          } catch (err) {
            alert("复制失败");
          }
          document.body.removeChild(textArea);
        }
      },
      // 选择支付方式
      selectMethod(methodId) {
        this.currentMethod = methodId;
      },
      // 获取当前支付方式名称
      getCurrentMethodName() {
        const method = this.paymentMethods.find((m) => m.value === this.currentMethod);
        return method ? method.name : "";
      },
      // 确认支付
      confirmPayment() {
        this.showPaymentModal = true;
      },
      // 取消支付
      cancelPayment() {
        this.showPaymentModal = false;
      },
      // 处理支付
      processPayment() {
        if (this.isProcessing)
          return;
        this.isProcessing = true;
        this.showPaymentModal = false;
        this.showLoading("正在处理支付...");
        setTimeout(async () => {
          try {
            if (this.orderInfo.orderNo) {
              const orderNos = String(this.orderInfo.orderNo).split(",").filter(Boolean);
              for (const on of orderNos) {
                const response = await request$1.post(`/api/app/order/${on}/pay-success`, {
                  user_id: getUserId(),
                  payment_method: this.currentMethod
                });
                if (response.data.code !== 200) {
                  throw new Error(response.data.message || "支付失败");
                }
              }
              this.hideLoading();
              this.paymentSuccess();
            } else {
              throw new Error("订单号不存在");
            }
          } catch (error) {
            formatAppLog("error", "at pages/payment/payment.vue:237", "支付处理失败:", error);
            this.hideLoading();
            this.paymentFail(error);
          }
        }, 2e3);
      },
      // 显示加载状态
      showLoading(message) {
        const loading = document.createElement("div");
        loading.className = "loading-overlay";
        loading.innerHTML = `
					<view class="loading-content">
						<view class="loading-spinner"></view>
						<view class="loading-text">${message}</view>
					</view>
				`;
        document.body.appendChild(loading);
      },
      // 隐藏加载状态
      hideLoading() {
        const loading = document.querySelector(".loading-overlay");
        if (loading) {
          document.body.removeChild(loading);
        }
      },
      // 支付成功处理
      paymentSuccess() {
        uni.navigateTo({
          url: "/pages/pay-result/pay-result?status=success&order_number=" + this.orderInfo.orderNo + "&total_amount=" + this.orderInfo.totalAmount
        });
      },
      // 支付失败处理
      paymentFail(err) {
        formatAppLog("error", "at pages/payment/payment.vue:276", "支付失败:", err);
        alert("支付失败：" + (err.message || "支付过程中出现问题"));
      }
    }
  };
  function _sfc_render$a(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "payment-container" }, [
      vue.createCommentVNode(" 头部 "),
      vue.createElementVNode("view", { class: "header" }, [
        vue.createElementVNode("view", {
          class: "back-btn",
          onClick: _cache[0] || (_cache[0] = (...args) => $options.goBack && $options.goBack(...args))
        }, [
          vue.createElementVNode("text", null, "←")
        ]),
        vue.createElementVNode("view", { class: "title" }, "支付订单")
      ]),
      vue.createCommentVNode(" 订单信息 "),
      vue.createElementVNode("view", { class: "order-info" }, [
        vue.createElementVNode("view", { class: "info-item" }, [
          vue.createElementVNode("text", { class: "label" }, "订单编号："),
          vue.createElementVNode(
            "text",
            { class: "value" },
            vue.toDisplayString($data.orderInfo.orderNo),
            1
            /* TEXT */
          ),
          vue.createElementVNode("text", {
            class: "copy-btn",
            onClick: _cache[1] || (_cache[1] = (...args) => $options.copyOrderNo && $options.copyOrderNo(...args))
          }, "复制")
        ]),
        vue.createElementVNode("view", { class: "info-item" }, [
          vue.createElementVNode("text", { class: "label" }, "创建时间："),
          vue.createElementVNode(
            "text",
            { class: "value" },
            vue.toDisplayString($data.orderInfo.createTime),
            1
            /* TEXT */
          )
        ]),
        vue.createElementVNode("view", { class: "info-item" }, [
          vue.createElementVNode("text", { class: "label" }, "商品名称："),
          vue.createElementVNode(
            "text",
            { class: "value" },
            vue.toDisplayString($data.orderInfo.productName),
            1
            /* TEXT */
          )
        ]),
        vue.createElementVNode("view", { class: "info-item" }, [
          vue.createElementVNode("text", { class: "label" }, "应付金额："),
          vue.createElementVNode(
            "text",
            { class: "price" },
            "¥" + vue.toDisplayString($data.orderInfo.totalAmount),
            1
            /* TEXT */
          )
        ])
      ]),
      vue.createCommentVNode(" 支付方式选择 "),
      vue.createElementVNode("view", { class: "payment-methods" }, [
        vue.createElementVNode("view", { class: "section-title" }, "支付方式"),
        vue.createElementVNode("view", { class: "method-list" }, [
          (vue.openBlock(true), vue.createElementBlock(
            vue.Fragment,
            null,
            vue.renderList($data.paymentMethods, (method) => {
              return vue.openBlock(), vue.createElementBlock("view", {
                class: vue.normalizeClass(["method-item", { selected: method.value === $data.currentMethod }]),
                key: method.value,
                onClick: ($event) => $options.selectMethod(method.value)
              }, [
                vue.createElementVNode("view", { class: "method-left" }, [
                  vue.createElementVNode("view", { class: "method-icon" }, [
                    vue.createElementVNode(
                      "text",
                      {
                        class: vue.normalizeClass(method.icon)
                      },
                      null,
                      2
                      /* CLASS */
                    )
                  ]),
                  vue.createElementVNode("view", { class: "method-info" }, [
                    vue.createElementVNode(
                      "view",
                      { class: "method-name" },
                      vue.toDisplayString(method.name),
                      1
                      /* TEXT */
                    ),
                    vue.createElementVNode(
                      "view",
                      { class: "method-desc" },
                      vue.toDisplayString(method.description),
                      1
                      /* TEXT */
                    )
                  ])
                ]),
                vue.createElementVNode("view", { class: "method-right" }, [
                  vue.createElementVNode(
                    "view",
                    {
                      class: vue.normalizeClass(["radio-btn", { active: method.value === $data.currentMethod }])
                    },
                    [
                      vue.createElementVNode("text", { class: "radio-inner" })
                    ],
                    2
                    /* CLASS */
                  )
                ])
              ], 10, ["onClick"]);
            }),
            128
            /* KEYED_FRAGMENT */
          ))
        ])
      ]),
      vue.createCommentVNode(" 底部支付按钮 "),
      vue.createElementVNode("view", { class: "payment-footer" }, [
        vue.createElementVNode("view", { class: "price-info" }, [
          vue.createElementVNode("text", null, "应付："),
          vue.createElementVNode(
            "text",
            { class: "price" },
            "¥" + vue.toDisplayString($data.orderInfo.totalAmount),
            1
            /* TEXT */
          )
        ]),
        vue.createElementVNode("view", {
          class: "pay-btn",
          onClick: _cache[2] || (_cache[2] = (...args) => $options.confirmPayment && $options.confirmPayment(...args))
        }, "立即支付")
      ]),
      vue.createCommentVNode(" 支付确认弹窗 "),
      $data.showPaymentModal ? (vue.openBlock(), vue.createElementBlock("view", {
        key: 0,
        class: "payment-modal"
      }, [
        vue.createElementVNode("view", { class: "modal-content" }, [
          vue.createElementVNode("view", { class: "modal-header" }, [
            vue.createElementVNode("h3", null, "确认支付")
          ]),
          vue.createElementVNode("view", { class: "modal-body" }, [
            vue.createElementVNode(
              "p",
              null,
              "订单号：" + vue.toDisplayString($data.orderInfo.orderNo),
              1
              /* TEXT */
            ),
            vue.createElementVNode(
              "p",
              null,
              "支付金额：¥" + vue.toDisplayString($data.orderInfo.totalAmount),
              1
              /* TEXT */
            ),
            vue.createElementVNode(
              "p",
              null,
              "支付方式：" + vue.toDisplayString($options.getCurrentMethodName()),
              1
              /* TEXT */
            )
          ]),
          vue.createElementVNode("view", { class: "modal-footer" }, [
            vue.createElementVNode("button", {
              class: "cancel-btn",
              onClick: _cache[3] || (_cache[3] = (...args) => $options.cancelPayment && $options.cancelPayment(...args))
            }, "取消"),
            vue.createElementVNode("button", {
              class: "confirm-btn",
              onClick: _cache[4] || (_cache[4] = (...args) => $options.processPayment && $options.processPayment(...args))
            }, "确认支付")
          ])
        ])
      ])) : vue.createCommentVNode("v-if", true)
    ]);
  }
  const PagesPaymentPayment = /* @__PURE__ */ _export_sfc(_sfc_main$b, [["render", _sfc_render$a], ["__scopeId", "data-v-eade9ab2"], ["__file", "/Users/chenjianping/Desktop/private/pro/sheng/yinjiajia/app/front-app-uni/pages/payment/payment.vue"]]);
  const _sfc_main$a = {
    name: "Login",
    data() {
      return {
        phone: "",
        password: ""
      };
    },
    methods: {
      handleSubmit() {
        authApi.login({
          phone: this.phone,
          password: this.password
        }).then((res) => {
          formatAppLog("log", "at pages/login/login.vue:53", "登录响应:", res);
          if (res.data.code === 200) {
            const { token, expires_at, user_id, user_number, phone } = res.data.data;
            setUser({ user_id, user_number, phone });
            setToken(token, expires_at);
            uni.switchTab({
              url: "/pages/shop/shop",
              fail: (err) => {
                uni.showToast({
                  title: "跳转失败",
                  icon: "none"
                });
              }
            });
          } else {
            uni.showToast({
              title: res.data.message || "登录失败",
              icon: "none"
            });
          }
        }).catch((err) => {
          formatAppLog("error", "at pages/login/login.vue:75", "登录请求失败:", err);
          uni.showToast({
            title: "网络错误",
            icon: "none"
          });
        });
      }
    }
  };
  function _sfc_render$9(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "login-container" }, [
      vue.createElementVNode("view", { class: "header" }, [
        vue.createElementVNode("text", { class: "title" }, "登录")
      ]),
      vue.createElementVNode("view", { class: "form" }, [
        vue.createElementVNode("view", { class: "field" }, [
          vue.createElementVNode("text", { class: "label" }, "手机号"),
          vue.withDirectives(vue.createElementVNode(
            "input",
            {
              "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => $data.phone = $event),
              type: "text",
              placeholder: "请输入手机号",
              class: "input"
            },
            null,
            512
            /* NEED_PATCH */
          ), [
            [vue.vModelText, $data.phone]
          ])
        ]),
        vue.createElementVNode("view", { class: "field" }, [
          vue.createElementVNode("text", { class: "label" }, "密码"),
          vue.withDirectives(vue.createElementVNode(
            "input",
            {
              "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => $data.password = $event),
              type: "text",
              placeholder: "请输入密码",
              class: "input"
            },
            null,
            512
            /* NEED_PATCH */
          ), [
            [vue.vModelText, $data.password]
          ])
        ]),
        vue.createElementVNode("button", {
          class: "submit",
          onClick: _cache[2] || (_cache[2] = (...args) => $options.handleSubmit && $options.handleSubmit(...args))
        }, " 登录 ")
      ])
    ]);
  }
  const PagesLoginLogin = /* @__PURE__ */ _export_sfc(_sfc_main$a, [["render", _sfc_render$9], ["__scopeId", "data-v-e4e4508d"], ["__file", "/Users/chenjianping/Desktop/private/pro/sheng/yinjiajia/app/front-app-uni/pages/login/login.vue"]]);
  const _sfc_main$9 = {
    name: "Register",
    data() {
      return {
        phone: "",
        password: "",
        submitting: false
      };
    },
    methods: {
      validate() {
        if (!this.phone || !this.password) {
          alert("请输入手机号和密码");
          return false;
        }
        if (!/^\+?\d[\d\s-]{5,}$/.test(this.phone)) {
          alert("手机号格式不正确");
          return false;
        }
        if (this.password.length < 6) {
          alert("密码至少6位");
          return false;
        }
        return true;
      },
      async handleSubmit() {
        if (!this.validate())
          return;
        this.submitting = true;
        try {
          const res = await authApi.register({ phone: this.phone, password: this.password });
          if (res.data.code === 200) {
            uni.showToast({
              title: "注册成功，请登录",
              icon: "success"
            });
            uni.redirectTo({
              url: "/pages/login/login"
            });
          } else {
            uni.showToast({
              title: res.data.message || "注册失败",
              icon: "error"
            });
          }
        } catch (e) {
          formatAppLog("error", "at pages/register/register.vue:79", "注册失败:", e);
          uni.showToast({
            title: "网络错误，注册失败",
            icon: "error"
          });
        } finally {
          this.submitting = false;
        }
      },
      goLogin() {
        uni.redirectTo({
          url: "/pages/login/login"
        });
      }
    }
  };
  function _sfc_render$8(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "register-container" }, [
      vue.createElementVNode("view", { class: "header" }, [
        vue.createElementVNode("h1", null, "注册"),
        vue.createElementVNode("p", null, "使用手机号与密码创建账户")
      ]),
      vue.createElementVNode(
        "form",
        {
          class: "form",
          onSubmit: _cache[2] || (_cache[2] = vue.withModifiers((...args) => $options.handleSubmit && $options.handleSubmit(...args), ["prevent"]))
        },
        [
          vue.createElementVNode("label", { class: "field" }, [
            vue.createElementVNode("text", null, "手机号"),
            vue.withDirectives(vue.createElementVNode(
              "input",
              {
                "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => $data.phone = $event),
                type: "tel",
                placeholder: "请输入手机号",
                maxlength: "20"
              },
              null,
              512
              /* NEED_PATCH */
            ), [
              [
                vue.vModelText,
                $data.phone,
                void 0,
                { trim: true }
              ]
            ])
          ]),
          vue.createElementVNode("label", { class: "field" }, [
            vue.createElementVNode("text", null, "密码"),
            vue.withDirectives(vue.createElementVNode(
              "input",
              {
                "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => $data.password = $event),
                type: "password",
                placeholder: "请输入密码",
                maxlength: "50"
              },
              null,
              512
              /* NEED_PATCH */
            ), [
              [vue.vModelText, $data.password]
            ])
          ]),
          vue.createElementVNode("button", {
            class: "submit",
            disabled: $data.submitting,
            type: "submit"
          }, vue.toDisplayString($data.submitting ? "提交中..." : "注册"), 9, ["disabled"])
        ],
        32
        /* NEED_HYDRATION */
      ),
      vue.createElementVNode("view", { class: "footer" }, [
        vue.createElementVNode("text", null, "已有账号？"),
        vue.createElementVNode("a", {
          onClick: _cache[3] || (_cache[3] = vue.withModifiers((...args) => $options.goLogin && $options.goLogin(...args), ["prevent"])),
          href: "#"
        }, "去登录")
      ])
    ]);
  }
  const PagesRegisterRegister = /* @__PURE__ */ _export_sfc(_sfc_main$9, [["render", _sfc_render$8], ["__scopeId", "data-v-bac4a35d"], ["__file", "/Users/chenjianping/Desktop/private/pro/sheng/yinjiajia/app/front-app-uni/pages/register/register.vue"]]);
  const _sfc_main$8 = {
    name: "MyOrder",
    data() {
      return {
        user_id: getUserId(),
        currentStatus: "",
        currentPage: 1,
        perPage: 10,
        orders: [],
        loading: false,
        hasNextPage: false,
        statusOptions: [
          { label: "全部", value: "" },
          { label: "待付款", value: "pending" },
          { label: "已付款", value: "paid" },
          { label: "已发货", value: "shipped" },
          { label: "已完成", value: "completed" },
          { label: "已取消", value: "cancelled" },
          { label: "已退款", value: "refunded" }
        ]
      };
    },
    mounted() {
      this.loadOrders();
    },
    activated() {
      this.loadOrders();
    },
    methods: {
      // 金额格式化
      formatPrice(val) {
        const n = Number(val || 0);
        return n.toFixed(2);
      },
      // 根据商家分组；若后端暂未返回商家信息，则聚合为单组
      groupItemsByMerchant(items = []) {
        if (!items || items.length === 0)
          return [];
        const groupsMap = /* @__PURE__ */ new Map();
        items.forEach((it) => {
          const key = it.merchant_id || "unknown";
          const name = it.merchant_name || "商家";
          if (!groupsMap.has(key)) {
            groupsMap.set(key, {
              key,
              merchantName: name,
              items: [],
              totalAmount: 0,
              totalCount: 0
            });
          }
          const g = groupsMap.get(key);
          g.items.push(it);
          g.totalAmount += Number(it.subtotal || (it.price || 0) * (it.quantity || 0));
          g.totalCount += Number(it.quantity || 0);
        });
        const groups = Array.from(groupsMap.values()).map((g) => {
          const preview = g.items.slice(0, 2).map((x) => x.product_image || "/static/default-product.png");
          return { ...g, previewImages: preview };
        });
        return groups;
      },
      // 返回上一页
      goBack() {
        uni.navigateBack({
          delta: 1
        });
      },
      // 选择状态筛选
      selectStatus(status) {
        this.currentStatus = status;
        this.currentPage = 1;
        this.orders = [];
        this.loadOrders();
      },
      // 加载订单列表
      async loadOrders() {
        if (this.loading)
          return;
        this.loading = true;
        try {
          const params = {
            user_id: this.user_id,
            page: this.currentPage,
            per_page: this.perPage
          };
          if (this.currentStatus) {
            params.status = this.currentStatus;
          }
          const response = await request$1.get("/api/app/order/", { params });
          if (response.data.code === 200) {
            const data = response.data.data;
            if (this.currentPage === 1) {
              this.orders = data.list;
            } else {
              this.orders = [...this.orders, ...data.list];
            }
            this.hasNextPage = data.pagination.has_next;
          }
        } catch (error) {
          formatAppLog("error", "at pages/myorder/myorder.vue:220", "加载订单列表失败:", error);
          uni.showToast({
            title: "加载订单列表失败",
            icon: "error"
          });
        } finally {
          this.loading = false;
        }
      },
      // 加载更多
      loadMore() {
        if (this.hasNextPage && !this.loading) {
          this.currentPage++;
          this.loadOrders();
        }
      },
      // 格式化日期
      formatDate(dateString) {
        if (!dateString)
          return "";
        const date = new Date(dateString);
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, "0");
        const day = date.getDate().toString().padStart(2, "0");
        const hours = date.getHours().toString().padStart(2, "0");
        const minutes = date.getMinutes().toString().padStart(2, "0");
        return `${year}-${month}-${day} ${hours}:${minutes}`;
      },
      // 获取状态样式类
      getStatusClass(status) {
        const statusClassMap = {
          "pending": "status-pending",
          "paid": "status-paid",
          "shipped": "status-shipped",
          "completed": "status-completed",
          "cancelled": "status-cancelled",
          "refunded": "status-refunded"
        };
        return statusClassMap[status] || "status-default";
      },
      // 获取商品总数量
      getTotalQuantity(items) {
        return items.reduce((total, item) => total + item.quantity, 0);
      },
      // 获取规格文本（简化处理）
      getSpecText(specCombinationId) {
        return "默认规格";
      },
      // 查看订单详情
      viewOrderDetail(orderId) {
        uni.navigateTo({
          url: `/pages/order-detail/order-detail?id=${orderId}`
        });
      },
      // 去支付
      goPay(order) {
        uni.navigateTo({
          url: `/pages/payment/payment?order_number=${order.order_number}&total_amount=${order.total_amount}`
        });
      },
      // 取消订单
      async cancelOrder(order) {
        uni.showModal({
          title: "确认取消",
          content: "确定取消该订单吗？",
          success: async (res) => {
            var _a;
            if (res.confirm) {
              try {
                const res2 = await request$1.post(`/api/app/order/${order.id}/cancel`, null, { params: { user_id: this.user_id } });
                if (res2.data && res2.data.code === 200) {
                  uni.showToast({
                    title: "订单已取消",
                    icon: "success"
                  });
                  this.currentPage = 1;
                  this.orders = [];
                  await this.loadOrders();
                } else {
                  uni.showToast({
                    title: ((_a = res2.data) == null ? void 0 : _a.message) || "取消失败",
                    icon: "error"
                  });
                }
              } catch (e) {
                formatAppLog("error", "at pages/myorder/myorder.vue:314", "取消订单失败", e);
                uni.showToast({
                  title: "取消失败",
                  icon: "error"
                });
              }
            }
          }
        });
      },
      // 售后（占位）
      afterSales(order) {
        uni.showToast({
          title: "售后功能开发中...",
          icon: "none"
        });
      },
      // 查看物流
      viewLogistics(order) {
        if (order.logistics) {
          const logistics = order.logistics;
          const message = `物流公司：${logistics.carrier}
物流单号：${logistics.tracking_number}
物流状态：${logistics.status_text || logistics.status}`;
          uni.showModal({
            title: "物流信息",
            content: message,
            showCancel: false
          });
        } else {
          uni.showToast({
            title: "暂无物流信息",
            icon: "none"
          });
        }
      },
      // 确认收货
      async confirmReceipt(order) {
        uni.showModal({
          title: "确认收货",
          content: "确认已收到货物吗？",
          success: async (res) => {
            var _a;
            if (res.confirm) {
              try {
                const res2 = await request$1.post(`/api/app/order/${order.id}/confirm-receipt`, {
                  user_id: this.user_id
                });
                if (res2.data && res2.data.code === 200) {
                  uni.showToast({
                    title: "确认收货成功",
                    icon: "success"
                  });
                  this.currentPage = 1;
                  this.orders = [];
                  await this.loadOrders();
                } else {
                  uni.showToast({
                    title: ((_a = res2.data) == null ? void 0 : _a.message) || "确认收货失败",
                    icon: "error"
                  });
                }
              } catch (e) {
                formatAppLog("error", "at pages/myorder/myorder.vue:378", "确认收货失败", e);
                uni.showToast({
                  title: "确认收货失败",
                  icon: "error"
                });
              }
            }
          }
        });
      },
      // 去购物
      goShop() {
        uni.switchTab({
          url: "/pages/index/index"
        });
      }
    }
  };
  function _sfc_render$7(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "order-list-container" }, [
      vue.createCommentVNode(" 头部 "),
      vue.createElementVNode("view", { class: "header" }, [
        vue.createElementVNode("view", {
          class: "back-btn",
          onClick: _cache[0] || (_cache[0] = (...args) => $options.goBack && $options.goBack(...args))
        }, [
          vue.createElementVNode("text", null, "←")
        ]),
        vue.createElementVNode("view", { class: "title" }, "我的订单")
      ]),
      vue.createCommentVNode(" 状态筛选 "),
      vue.createElementVNode("view", { class: "status-filter" }, [
        (vue.openBlock(true), vue.createElementBlock(
          vue.Fragment,
          null,
          vue.renderList($data.statusOptions, (status) => {
            return vue.openBlock(), vue.createElementBlock("view", {
              class: vue.normalizeClass(["filter-item", { active: $data.currentStatus === status.value }]),
              key: status.value,
              onClick: ($event) => $options.selectStatus(status.value)
            }, vue.toDisplayString(status.label), 11, ["onClick"]);
          }),
          128
          /* KEYED_FRAGMENT */
        ))
      ]),
      vue.createCommentVNode(" 订单列表 "),
      $data.orders.length > 0 ? (vue.openBlock(), vue.createElementBlock("view", {
        key: 0,
        class: "order-list"
      }, [
        (vue.openBlock(true), vue.createElementBlock(
          vue.Fragment,
          null,
          vue.renderList($data.orders, (order) => {
            return vue.openBlock(), vue.createElementBlock("view", {
              class: "order-item",
              key: order.id,
              onClick: ($event) => $options.viewOrderDetail(order.id)
            }, [
              vue.createCommentVNode(" 商家分组列表（每个商家显示前2张图 + 件数 + 小计） "),
              vue.createElementVNode("view", { class: "merchant-groups" }, [
                (vue.openBlock(true), vue.createElementBlock(
                  vue.Fragment,
                  null,
                  vue.renderList($options.groupItemsByMerchant(order.items), (group) => {
                    return vue.openBlock(), vue.createElementBlock("view", {
                      class: "merchant-card",
                      key: group.key
                    }, [
                      vue.createElementVNode("view", { class: "merchant-header" }, [
                        vue.createElementVNode("view", { class: "row-top" }, [
                          vue.createElementVNode(
                            "view",
                            { class: "merchant-name" },
                            vue.toDisplayString(group.merchantName),
                            1
                            /* TEXT */
                          ),
                          vue.createElementVNode(
                            "view",
                            {
                              class: vue.normalizeClass(["order-status", $options.getStatusClass(order.status)])
                            },
                            vue.toDisplayString(order.status_text),
                            3
                            /* TEXT, CLASS */
                          )
                        ]),
                        vue.createElementVNode("view", { class: "merchant-meta" }, [
                          vue.createElementVNode(
                            "text",
                            null,
                            "共" + vue.toDisplayString(group.totalCount) + "件",
                            1
                            /* TEXT */
                          ),
                          vue.createElementVNode("text", { class: "split" }, "|"),
                          vue.createElementVNode(
                            "text",
                            null,
                            "小计 ¥" + vue.toDisplayString($options.formatPrice(group.totalAmount)),
                            1
                            /* TEXT */
                          )
                        ])
                      ]),
                      vue.createElementVNode("view", { class: "merchant-body" }, [
                        vue.createElementVNode("view", { class: "row-preview" }, [
                          vue.createElementVNode("view", { class: "preview-left" }, [
                            group.items.length === 1 ? (vue.openBlock(), vue.createElementBlock(
                              vue.Fragment,
                              { key: 0 },
                              [
                                vue.createElementVNode("view", { class: "preview single" }, [
                                  vue.createElementVNode("image", {
                                    src: group.items[0].product_image || "/static/default-product.png"
                                  }, null, 8, ["src"])
                                ]),
                                vue.createElementVNode("view", { class: "single-info" }, [
                                  vue.createElementVNode(
                                    "view",
                                    { class: "single-name" },
                                    vue.toDisplayString(group.items[0].product_name),
                                    1
                                    /* TEXT */
                                  ),
                                  vue.createElementVNode(
                                    "view",
                                    { class: "single-quantity" },
                                    "×" + vue.toDisplayString(group.items[0].quantity),
                                    1
                                    /* TEXT */
                                  )
                                ])
                              ],
                              64
                              /* STABLE_FRAGMENT */
                            )) : (vue.openBlock(), vue.createElementBlock("view", {
                              key: 1,
                              class: "preview-images"
                            }, [
                              (vue.openBlock(true), vue.createElementBlock(
                                vue.Fragment,
                                null,
                                vue.renderList(group.previewImages, (img, idx) => {
                                  return vue.openBlock(), vue.createElementBlock("view", {
                                    class: "preview",
                                    key: idx
                                  }, [
                                    vue.createElementVNode("image", { src: img }, null, 8, ["src"])
                                  ]);
                                }),
                                128
                                /* KEYED_FRAGMENT */
                              ))
                            ]))
                          ]),
                          vue.createElementVNode("view", { class: "summary" }, [
                            vue.createElementVNode(
                              "view",
                              { class: "count" },
                              "共" + vue.toDisplayString(group.totalCount) + "件",
                              1
                              /* TEXT */
                            ),
                            vue.createElementVNode(
                              "view",
                              { class: "amount" },
                              "合计 ¥" + vue.toDisplayString($options.formatPrice(group.totalAmount)),
                              1
                              /* TEXT */
                            )
                          ])
                        ]),
                        vue.createElementVNode("view", { class: "row-actions" }, [
                          vue.createElementVNode("view", { class: "order-actions" }, [
                            order.status === "pending" ? (vue.openBlock(), vue.createElementBlock("button", {
                              key: 0,
                              class: "action-btn primary",
                              onClick: vue.withModifiers(($event) => $options.goPay(order), ["stop"])
                            }, "去支付", 8, ["onClick"])) : vue.createCommentVNode("v-if", true),
                            order.status === "pending" || order.status === "paid" ? (vue.openBlock(), vue.createElementBlock("button", {
                              key: 1,
                              class: "action-btn secondary",
                              onClick: vue.withModifiers(($event) => $options.cancelOrder(order), ["stop"])
                            }, "取消订单", 8, ["onClick"])) : vue.createCommentVNode("v-if", true),
                            order.status === "shipped" || order.status === "delivered" ? (vue.openBlock(), vue.createElementBlock("button", {
                              key: 2,
                              class: "action-btn secondary",
                              onClick: vue.withModifiers(($event) => $options.viewLogistics(order), ["stop"])
                            }, "查看物流", 8, ["onClick"])) : vue.createCommentVNode("v-if", true),
                            order.status === "shipped" || order.status === "delivered" ? (vue.openBlock(), vue.createElementBlock("button", {
                              key: 3,
                              class: "action-btn primary",
                              onClick: vue.withModifiers(($event) => $options.confirmReceipt(order), ["stop"])
                            }, "确认收货", 8, ["onClick"])) : vue.createCommentVNode("v-if", true),
                            order.status === "delivered" || order.status === "completed" ? (vue.openBlock(), vue.createElementBlock("button", {
                              key: 4,
                              class: "action-btn secondary",
                              onClick: vue.withModifiers(($event) => $options.afterSales(order), ["stop"])
                            }, "售后", 8, ["onClick"])) : vue.createCommentVNode("v-if", true)
                          ])
                        ])
                      ])
                    ]);
                  }),
                  128
                  /* KEYED_FRAGMENT */
                ))
              ]),
              vue.createCommentVNode(" 订单底部 "),
              vue.createCommentVNode(' <view class="order-footer">\n          <view class="order-total">\n            <text>共{{ getTotalQuantity(order.items) }}件商品</text>\n            <text class="total-price">合计：¥{{ order.total_amount }}</text>\n          </view>\n        </view> ')
            ], 8, ["onClick"]);
          }),
          128
          /* KEYED_FRAGMENT */
        ))
      ])) : (vue.openBlock(), vue.createElementBlock(
        vue.Fragment,
        { key: 1 },
        [
          vue.createCommentVNode(" 空状态 "),
          vue.createElementVNode("view", { class: "empty-state" }, [
            vue.createElementVNode("view", { class: "empty-text" }, "暂无订单"),
            vue.createElementVNode("button", {
              class: "go-shop-btn",
              onClick: _cache[1] || (_cache[1] = (...args) => $options.goShop && $options.goShop(...args))
            }, "去购物")
          ])
        ],
        2112
        /* STABLE_FRAGMENT, DEV_ROOT_FRAGMENT */
      )),
      vue.createCommentVNode(" 加载更多 "),
      $data.hasNextPage && $data.orders.length > 0 ? (vue.openBlock(), vue.createElementBlock("view", {
        key: 2,
        class: "load-more"
      }, [
        vue.createElementVNode("button", {
          class: "load-more-btn",
          onClick: _cache[2] || (_cache[2] = (...args) => $options.loadMore && $options.loadMore(...args)),
          disabled: $data.loading
        }, vue.toDisplayString($data.loading ? "加载中..." : "加载更多"), 9, ["disabled"])
      ])) : vue.createCommentVNode("v-if", true)
    ]);
  }
  const PagesMyorderMyorder = /* @__PURE__ */ _export_sfc(_sfc_main$8, [["render", _sfc_render$7], ["__scopeId", "data-v-ba124ed0"], ["__file", "/Users/chenjianping/Desktop/private/pro/sheng/yinjiajia/app/front-app-uni/pages/myorder/myorder.vue"]]);
  const _sfc_main$7 = {
    name: "Address",
    components: {
      ConfirmModal
    },
    data() {
      return {
        addresses: [],
        showModal: false,
        isEditing: false,
        editingAddressId: null,
        fromPage: "",
        // 记录来源页面
        showDeleteModal: false,
        // 显示删除确认弹窗
        deleteAddressId: null,
        // 要删除的地址ID
        deleteAddressName: "",
        // 要删除的地址名称
        addressForm: {
          receiver_name: "",
          phone: "",
          province: "",
          city: "",
          district: "",
          detail_address: "",
          is_default: false
        }
      };
    },
    computed: {
      deleteConfirmContent() {
        return `确定要删除地址"${this.deleteAddressName}"吗？`;
      }
    },
    onLoad(options) {
      if (options.from) {
        this.fromPage = options.from;
      }
      this.loadAddresses();
    },
    methods: {
      goBack() {
        uni.navigateBack();
      },
      async loadAddresses() {
        try {
          const response = await request$1.get("/api/app/address/", {
            params: { user_id: getUserId() }
          });
          if (response.data.code === 200) {
            this.addresses = response.data.data;
          }
        } catch (error) {
          formatAppLog("error", "at pages/address/address.vue:202", "加载地址失败:", error);
        }
      },
      showAddAddress() {
        this.isEditing = false;
        this.editingAddressId = null;
        this.resetForm();
        this.showModal = true;
      },
      editAddress(address) {
        this.isEditing = true;
        this.editingAddressId = address.id;
        this.addressForm = { ...address };
        this.showModal = true;
      },
      async deleteAddress(address) {
        this.deleteAddressId = address.id;
        this.deleteAddressName = address.receiver_name;
        this.showDeleteModal = true;
      },
      async performDeleteAddress() {
        try {
          const response = await request$1.delete(`/api/app/address/${this.deleteAddressId}`);
          if (response.data.code === 200) {
            this.loadAddresses();
            this.showDeleteModal = false;
            this.deleteAddressId = null;
            this.deleteAddressName = "";
          }
        } catch (error) {
          formatAppLog("error", "at pages/address/address.vue:238", "删除地址失败:", error);
        }
      },
      async saveAddress() {
        if (!this.addressForm.receiver_name) {
          uni.showToast({
            title: "请输入收货人姓名",
            icon: "error"
          });
          return;
        }
        if (!this.addressForm.phone) {
          uni.showToast({
            title: "请输入手机号",
            icon: "error"
          });
          return;
        }
        if (!this.addressForm.province || !this.addressForm.city || !this.addressForm.district) {
          uni.showToast({
            title: "请完善地址信息",
            icon: "error"
          });
          return;
        }
        if (!this.addressForm.detail_address) {
          uni.showToast({
            title: "请输入详细地址",
            icon: "error"
          });
          return;
        }
        try {
          const data = {
            user_id: getUserId(),
            ...this.addressForm
          };
          let response;
          if (this.isEditing) {
            response = await request$1.put(`/api/app/address/${this.editingAddressId}`, data);
          } else {
            response = await request$1.post("/api/app/address/", data);
          }
          if (response.data.code === 200) {
            this.closeModal();
            this.loadAddresses();
          }
        } catch (error) {
          formatAppLog("error", "at pages/address/address.vue:291", "保存地址失败:", error);
        }
      },
      selectAddress(address) {
        if (this.fromPage === "checkout") {
          uni.navigateBack();
        }
      },
      closeModal() {
        this.showModal = false;
        this.resetForm();
      },
      resetForm() {
        this.addressForm = {
          receiver_name: "",
          phone: "",
          province: "",
          city: "",
          district: "",
          detail_address: "",
          is_default: false
        };
      }
    }
  };
  function _sfc_render$6(_ctx, _cache, $props, $setup, $data, $options) {
    const _component_ConfirmModal = vue.resolveComponent("ConfirmModal");
    return vue.openBlock(), vue.createElementBlock(
      vue.Fragment,
      null,
      [
        vue.createElementVNode("view", { class: "address-container" }, [
          vue.createCommentVNode(" 头部 "),
          vue.createElementVNode("view", { class: "header" }, [
            vue.createElementVNode("view", {
              class: "back-btn",
              onClick: _cache[0] || (_cache[0] = (...args) => $options.goBack && $options.goBack(...args))
            }, [
              vue.createElementVNode("text", null, "←")
            ]),
            vue.createElementVNode("view", { class: "title" }, "收货地址"),
            vue.createElementVNode("view", {
              class: "add-btn",
              onClick: _cache[1] || (_cache[1] = (...args) => $options.showAddAddress && $options.showAddAddress(...args))
            }, [
              vue.createElementVNode("text", null, "+")
            ])
          ]),
          vue.createCommentVNode(" 地址列表 "),
          $data.addresses.length > 0 ? (vue.openBlock(), vue.createElementBlock("view", {
            key: 0,
            class: "address-list"
          }, [
            (vue.openBlock(true), vue.createElementBlock(
              vue.Fragment,
              null,
              vue.renderList($data.addresses, (address) => {
                return vue.openBlock(), vue.createElementBlock("view", {
                  class: "address-item",
                  key: address.id,
                  onClick: ($event) => $options.selectAddress(address)
                }, [
                  vue.createElementVNode("view", { class: "address-info" }, [
                    vue.createElementVNode("view", { class: "receiver-info" }, [
                      vue.createElementVNode(
                        "text",
                        { class: "receiver-name" },
                        vue.toDisplayString(address.receiver_name),
                        1
                        /* TEXT */
                      ),
                      vue.createElementVNode(
                        "text",
                        { class: "receiver-phone" },
                        vue.toDisplayString(address.phone),
                        1
                        /* TEXT */
                      ),
                      address.is_default ? (vue.openBlock(), vue.createElementBlock("text", {
                        key: 0,
                        class: "default-tag"
                      }, "默认")) : vue.createCommentVNode("v-if", true)
                    ]),
                    vue.createElementVNode(
                      "view",
                      { class: "address-detail" },
                      vue.toDisplayString(address.full_address),
                      1
                      /* TEXT */
                    )
                  ]),
                  vue.createElementVNode("view", { class: "address-actions" }, [
                    vue.createElementVNode("view", {
                      class: "action-btn edit-btn",
                      onClick: vue.withModifiers(($event) => $options.editAddress(address), ["stop"])
                    }, [
                      vue.createElementVNode("text", null, "✏️")
                    ], 8, ["onClick"]),
                    vue.createElementVNode("view", {
                      class: "action-btn delete-btn",
                      onClick: vue.withModifiers(($event) => $options.deleteAddress(address), ["stop"])
                    }, [
                      vue.createElementVNode("text", null, "��️")
                    ], 8, ["onClick"])
                  ])
                ], 8, ["onClick"]);
              }),
              128
              /* KEYED_FRAGMENT */
            ))
          ])) : (vue.openBlock(), vue.createElementBlock(
            vue.Fragment,
            { key: 1 },
            [
              vue.createCommentVNode(" 空状态 "),
              vue.createElementVNode("view", { class: "empty-state" }, [
                vue.createElementVNode("view", { class: "empty-text" }, "暂无收货地址"),
                vue.createElementVNode("view", { class: "empty-desc" }, "添加收货地址，享受便捷购物"),
                vue.createElementVNode("view", {
                  class: "add-address-btn",
                  onClick: _cache[2] || (_cache[2] = (...args) => $options.showAddAddress && $options.showAddAddress(...args))
                }, " 添加地址 ")
              ])
            ],
            2112
            /* STABLE_FRAGMENT, DEV_ROOT_FRAGMENT */
          )),
          vue.createCommentVNode(" 添加/编辑地址弹窗 "),
          $data.showModal ? (vue.openBlock(), vue.createElementBlock("view", {
            key: 2,
            class: "modal-overlay",
            onClick: _cache[14] || (_cache[14] = (...args) => $options.closeModal && $options.closeModal(...args))
          }, [
            vue.createElementVNode("view", {
              class: "modal-content",
              onClick: _cache[13] || (_cache[13] = vue.withModifiers(() => {
              }, ["stop"]))
            }, [
              vue.createElementVNode("view", { class: "modal-header" }, [
                vue.createElementVNode(
                  "view",
                  { class: "modal-title" },
                  vue.toDisplayString($data.isEditing ? "编辑地址" : "添加地址"),
                  1
                  /* TEXT */
                ),
                vue.createElementVNode("view", {
                  class: "close-btn",
                  onClick: _cache[3] || (_cache[3] = (...args) => $options.closeModal && $options.closeModal(...args))
                }, "×")
              ]),
              vue.createElementVNode("view", { class: "form-content" }, [
                vue.createElementVNode("view", { class: "form-item" }, [
                  vue.createElementVNode("label", null, "收货人"),
                  vue.withDirectives(vue.createElementVNode(
                    "input",
                    {
                      "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => $data.addressForm.receiver_name = $event),
                      placeholder: "请输入收货人姓名",
                      maxlength: "20"
                    },
                    null,
                    512
                    /* NEED_PATCH */
                  ), [
                    [vue.vModelText, $data.addressForm.receiver_name]
                  ])
                ]),
                vue.createElementVNode("view", { class: "form-item" }, [
                  vue.createElementVNode("label", null, "手机号"),
                  vue.withDirectives(vue.createElementVNode(
                    "input",
                    {
                      "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => $data.addressForm.phone = $event),
                      placeholder: "请输入手机号",
                      type: "tel",
                      maxlength: "11"
                    },
                    null,
                    512
                    /* NEED_PATCH */
                  ), [
                    [vue.vModelText, $data.addressForm.phone]
                  ])
                ]),
                vue.createElementVNode("view", { class: "form-item" }, [
                  vue.createElementVNode("label", null, "省份"),
                  vue.withDirectives(vue.createElementVNode(
                    "input",
                    {
                      "onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => $data.addressForm.province = $event),
                      placeholder: "请输入省份"
                    },
                    null,
                    512
                    /* NEED_PATCH */
                  ), [
                    [vue.vModelText, $data.addressForm.province]
                  ])
                ]),
                vue.createElementVNode("view", { class: "form-item" }, [
                  vue.createElementVNode("label", null, "城市"),
                  vue.withDirectives(vue.createElementVNode(
                    "input",
                    {
                      "onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => $data.addressForm.city = $event),
                      placeholder: "请输入城市"
                    },
                    null,
                    512
                    /* NEED_PATCH */
                  ), [
                    [vue.vModelText, $data.addressForm.city]
                  ])
                ]),
                vue.createElementVNode("view", { class: "form-item" }, [
                  vue.createElementVNode("label", null, "区县"),
                  vue.withDirectives(vue.createElementVNode(
                    "input",
                    {
                      "onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => $data.addressForm.district = $event),
                      placeholder: "请输入区县"
                    },
                    null,
                    512
                    /* NEED_PATCH */
                  ), [
                    [vue.vModelText, $data.addressForm.district]
                  ])
                ]),
                vue.createElementVNode("view", { class: "form-item" }, [
                  vue.createElementVNode("label", null, "详细地址"),
                  vue.withDirectives(vue.createElementVNode(
                    "textarea",
                    {
                      "onUpdate:modelValue": _cache[9] || (_cache[9] = ($event) => $data.addressForm.detail_address = $event),
                      placeholder: "请输入详细地址",
                      rows: "3"
                    },
                    null,
                    512
                    /* NEED_PATCH */
                  ), [
                    [vue.vModelText, $data.addressForm.detail_address]
                  ])
                ]),
                vue.createElementVNode("view", { class: "form-item checkbox-item" }, [
                  vue.createElementVNode("label", null, [
                    vue.withDirectives(vue.createElementVNode(
                      "input",
                      {
                        type: "checkbox",
                        "onUpdate:modelValue": _cache[10] || (_cache[10] = ($event) => $data.addressForm.is_default = $event)
                      },
                      null,
                      512
                      /* NEED_PATCH */
                    ), [
                      [vue.vModelCheckbox, $data.addressForm.is_default]
                    ]),
                    vue.createTextVNode(" 设为默认地址 ")
                  ])
                ])
              ]),
              vue.createElementVNode("view", { class: "modal-actions" }, [
                vue.createElementVNode("view", {
                  class: "cancel-btn",
                  onClick: _cache[11] || (_cache[11] = (...args) => $options.closeModal && $options.closeModal(...args))
                }, "取消"),
                vue.createElementVNode("view", {
                  class: "save-btn",
                  onClick: _cache[12] || (_cache[12] = (...args) => $options.saveAddress && $options.saveAddress(...args))
                }, "保存")
              ])
            ])
          ])) : vue.createCommentVNode("v-if", true)
        ]),
        vue.createCommentVNode(" 删除确认弹窗 "),
        vue.createVNode(_component_ConfirmModal, {
          visible: $data.showDeleteModal,
          title: "确认删除",
          content: $options.deleteConfirmContent,
          "confirm-text": "删除",
          "cancel-text": "取消",
          type: "delete",
          onConfirm: $options.performDeleteAddress,
          onCancel: _cache[15] || (_cache[15] = ($event) => $data.showDeleteModal = false)
        }, null, 8, ["visible", "content", "onConfirm"])
      ],
      64
      /* STABLE_FRAGMENT */
    );
  }
  const PagesAddressAddress = /* @__PURE__ */ _export_sfc(_sfc_main$7, [["render", _sfc_render$6], ["__scopeId", "data-v-40ca010a"], ["__file", "/Users/chenjianping/Desktop/private/pro/sheng/yinjiajia/app/front-app-uni/pages/address/address.vue"]]);
  const _sfc_main$6 = {
    name: "AddressList",
    data() {
      return {
        addressList: [],
        selectedAddressId: null,
        fromPage: ""
      };
    },
    onLoad(options) {
      this.fromPage = options.from || "";
      this.loadAddressList();
    },
    methods: {
      goBack() {
        uni.navigateBack();
      },
      async loadAddressList() {
        try {
          const response = await request$1.get("/api/app/address/", {
            params: { user_id: getUserId() }
          });
          if (response.data.code === 200) {
            this.addressList = response.data.data;
            const cached = AddressService.getSelectedAddress();
            if (cached) {
              const exist = this.addressList.find((addr) => String(addr.id) === String(cached.id));
              if (exist) {
                this.selectedAddressId = exist.id;
              }
            }
            if (!this.selectedAddressId) {
              const defaultAddress = this.addressList.find((addr) => addr.is_default);
              if (defaultAddress) {
                this.selectedAddressId = defaultAddress.id;
              }
            }
          }
        } catch (error) {
          formatAppLog("error", "at pages/address-list/address-list.vue:100", "加载地址列表失败:", error);
        }
      },
      selectAddress(address) {
        this.selectedAddressId = address.id;
        AddressService.setSelectedAddress(address);
        if (this.fromPage === "checkout" || this.fromPage === "product-detail") {
          uni.navigateBack();
        }
      },
      addAddress() {
        uni.navigateTo({
          url: "/pages/address/address"
        });
      },
      confirmAddress() {
        if (!this.selectedAddressId) {
          uni.showToast({
            title: "请选择收货地址",
            icon: "none"
          });
          return;
        }
        const selectedAddress = this.addressList.find((addr) => addr.id === this.selectedAddressId);
        AddressService.setSelectedAddress(selectedAddress);
        uni.navigateBack();
      }
    }
  };
  function _sfc_render$5(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "address-list-container" }, [
      vue.createCommentVNode(" 头部 "),
      vue.createElementVNode("view", { class: "header" }, [
        vue.createElementVNode("view", {
          class: "back-btn",
          onClick: _cache[0] || (_cache[0] = (...args) => $options.goBack && $options.goBack(...args))
        }, [
          vue.createElementVNode("text", null, "←")
        ]),
        vue.createElementVNode("view", { class: "title" }, "选择收货地址"),
        vue.createElementVNode("view", {
          class: "add-btn",
          onClick: _cache[1] || (_cache[1] = (...args) => $options.addAddress && $options.addAddress(...args))
        }, "新增")
      ]),
      vue.createCommentVNode(" 地址列表 "),
      $data.addressList.length > 0 ? (vue.openBlock(), vue.createElementBlock("view", {
        key: 0,
        class: "address-list"
      }, [
        (vue.openBlock(true), vue.createElementBlock(
          vue.Fragment,
          null,
          vue.renderList($data.addressList, (address) => {
            return vue.openBlock(), vue.createElementBlock("view", {
              class: vue.normalizeClass(["address-item", { selected: $data.selectedAddressId === address.id }]),
              key: address.id,
              onClick: ($event) => $options.selectAddress(address)
            }, [
              vue.createElementVNode("view", { class: "address-content" }, [
                vue.createElementVNode("view", { class: "receiver-info" }, [
                  vue.createElementVNode(
                    "text",
                    { class: "receiver-name" },
                    vue.toDisplayString(address.receiver_name),
                    1
                    /* TEXT */
                  ),
                  vue.createElementVNode(
                    "text",
                    { class: "receiver-phone" },
                    vue.toDisplayString(address.phone),
                    1
                    /* TEXT */
                  )
                ]),
                vue.createElementVNode(
                  "view",
                  { class: "address-detail" },
                  vue.toDisplayString(address.full_address),
                  1
                  /* TEXT */
                )
              ]),
              vue.createElementVNode("view", { class: "address-actions" }, [
                address.is_default ? (vue.openBlock(), vue.createElementBlock("view", {
                  key: 0,
                  class: "default-tag"
                }, "默认")) : vue.createCommentVNode("v-if", true),
                $data.selectedAddressId === address.id ? (vue.openBlock(), vue.createElementBlock("view", {
                  key: 1,
                  class: "select-icon"
                }, "✓")) : vue.createCommentVNode("v-if", true)
              ])
            ], 10, ["onClick"]);
          }),
          128
          /* KEYED_FRAGMENT */
        ))
      ])) : (vue.openBlock(), vue.createElementBlock(
        vue.Fragment,
        { key: 1 },
        [
          vue.createCommentVNode(" 空状态 "),
          vue.createElementVNode("view", { class: "empty-state" }, [
            vue.createElementVNode("view", { class: "empty-text" }, "暂无收货地址"),
            vue.createElementVNode("view", { class: "empty-desc" }, "请添加收货地址以便下单"),
            vue.createElementVNode("view", {
              class: "add-address-btn",
              onClick: _cache[2] || (_cache[2] = (...args) => $options.addAddress && $options.addAddress(...args))
            }, "添加地址")
          ])
        ],
        2112
        /* STABLE_FRAGMENT, DEV_ROOT_FRAGMENT */
      )),
      vue.createCommentVNode(" 底部确认按钮 "),
      $data.addressList.length > 0 ? (vue.openBlock(), vue.createElementBlock("view", {
        key: 2,
        class: "bottom-bar"
      }, [
        vue.createElementVNode(
          "view",
          {
            class: vue.normalizeClass(["confirm-btn", { disabled: !$data.selectedAddressId }]),
            onClick: _cache[3] || (_cache[3] = (...args) => $options.confirmAddress && $options.confirmAddress(...args))
          },
          " 确认选择 ",
          2
          /* CLASS */
        )
      ])) : vue.createCommentVNode("v-if", true)
    ]);
  }
  const PagesAddressListAddressList = /* @__PURE__ */ _export_sfc(_sfc_main$6, [["render", _sfc_render$5], ["__scopeId", "data-v-e9c26d8f"], ["__file", "/Users/chenjianping/Desktop/private/pro/sheng/yinjiajia/app/front-app-uni/pages/address-list/address-list.vue"]]);
  const _sfc_main$5 = {
    name: "OrderDetail",
    data() {
      return {
        order: { items: [] },
        orderId: null
      };
    },
    computed: {
      statusClass() {
        const m = {
          pending: "status-pending",
          paid: "status-paid",
          shipped: "status-shipped",
          delivered: "status-delivered",
          completed: "status-completed",
          cancelled: "status-cancelled",
          refunded: "status-refunded"
        };
        return m[this.order.status] || "status-default";
      }
    },
    onLoad(options) {
      this.orderId = options.id || options.order_id;
      this.loadDetail();
    },
    methods: {
      formatDate(v) {
        if (!v)
          return "";
        const d = new Date(v);
        const p = (n) => String(n).padStart(2, "0");
        return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`;
      },
      formatPrice(n) {
        return Number(n || 0).toFixed(2);
      },
      goBack() {
        uni.navigateBack({
          delta: 1
        });
      },
      async loadDetail() {
        var _a;
        const id = this.orderId;
        if (!id) {
          uni.showToast({
            title: "订单ID不能为空",
            icon: "error"
          });
          return;
        }
        try {
          const res = await request$1.get(`/api/app/order/${id}`, { params: { user_id: getUserId() } });
          if (res.data && res.data.code === 200) {
            this.order = res.data.data;
          } else {
            uni.showToast({
              title: ((_a = res.data) == null ? void 0 : _a.message) || "加载失败",
              icon: "error"
            });
          }
        } catch (error) {
          uni.showToast({
            title: "网络错误",
            icon: "error"
          });
        }
      }
    }
  };
  function _sfc_render$4(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "detail-container" }, [
      vue.createElementVNode("view", { class: "header" }, [
        vue.createElementVNode("view", {
          class: "back-btn",
          onClick: _cache[0] || (_cache[0] = (...args) => $options.goBack && $options.goBack(...args))
        }, "←"),
        vue.createElementVNode("view", { class: "title" }, "订单详情")
      ]),
      vue.createCommentVNode(" 订单信息 "),
      vue.createElementVNode("view", { class: "card" }, [
        vue.createElementVNode("view", { class: "row" }, [
          vue.createElementVNode("text", { class: "label" }, "订单号"),
          vue.createElementVNode(
            "text",
            { class: "value" },
            vue.toDisplayString($data.order.order_number),
            1
            /* TEXT */
          )
        ]),
        vue.createElementVNode("view", { class: "row" }, [
          vue.createElementVNode("text", { class: "label" }, "下单时间"),
          vue.createElementVNode(
            "text",
            { class: "value" },
            vue.toDisplayString($options.formatDate($data.order.created_at)),
            1
            /* TEXT */
          )
        ]),
        vue.createElementVNode("view", { class: "row" }, [
          vue.createElementVNode("text", { class: "label" }, "订单状态"),
          vue.createElementVNode(
            "text",
            {
              class: vue.normalizeClass(["value status", $options.statusClass])
            },
            vue.toDisplayString($data.order.status_text),
            3
            /* TEXT, CLASS */
          )
        ]),
        vue.createElementVNode("view", { class: "row total" }, [
          vue.createElementVNode("text", { class: "label" }, "合计"),
          vue.createElementVNode(
            "text",
            { class: "value price" },
            "¥" + vue.toDisplayString($options.formatPrice($data.order.total_amount)),
            1
            /* TEXT */
          )
        ])
      ]),
      vue.createCommentVNode(" 物流信息 "),
      $data.order.logistics ? (vue.openBlock(), vue.createElementBlock("view", {
        key: 0,
        class: "card"
      }, [
        vue.createElementVNode("view", { class: "card-title" }, "物流信息"),
        vue.createElementVNode("view", { class: "row" }, [
          vue.createElementVNode("text", { class: "label" }, "物流公司"),
          vue.createElementVNode(
            "text",
            { class: "value" },
            vue.toDisplayString($data.order.logistics.carrier),
            1
            /* TEXT */
          )
        ]),
        vue.createElementVNode("view", { class: "row" }, [
          vue.createElementVNode("text", { class: "label" }, "运单号"),
          vue.createElementVNode(
            "text",
            { class: "value" },
            vue.toDisplayString($data.order.logistics.tracking_number),
            1
            /* TEXT */
          )
        ]),
        vue.createElementVNode("view", { class: "row" }, [
          vue.createElementVNode("text", { class: "label" }, "状态"),
          vue.createElementVNode(
            "text",
            { class: "value" },
            vue.toDisplayString($data.order.logistics.status_text || $data.order.logistics.status),
            1
            /* TEXT */
          )
        ]),
        vue.createElementVNode("view", { class: "row" }, [
          vue.createElementVNode("text", { class: "label" }, "更新时间"),
          vue.createElementVNode(
            "text",
            { class: "value" },
            vue.toDisplayString($options.formatDate($data.order.logistics.updated_at)),
            1
            /* TEXT */
          )
        ])
      ])) : vue.createCommentVNode("v-if", true),
      vue.createCommentVNode(" 商品列表 "),
      vue.createElementVNode("view", { class: "card" }, [
        vue.createElementVNode("view", { class: "card-title" }, "商品列表"),
        (vue.openBlock(true), vue.createElementBlock(
          vue.Fragment,
          null,
          vue.renderList($data.order.items, (it) => {
            return vue.openBlock(), vue.createElementBlock("view", {
              class: "item",
              key: it.id
            }, [
              vue.createElementVNode("view", { class: "thumb" }, [
                vue.createElementVNode("image", {
                  src: it.product_image || "/static/default-product.png"
                }, null, 8, ["src"])
              ]),
              vue.createElementVNode("view", { class: "info" }, [
                vue.createElementVNode("view", {
                  class: "name",
                  title: it.product_name
                }, vue.toDisplayString(it.product_name), 9, ["title"]),
                it.spec_combination_id ? (vue.openBlock(), vue.createElementBlock(
                  "view",
                  {
                    key: 0,
                    class: "spec"
                  },
                  "规格：" + vue.toDisplayString(it.spec_combination_id),
                  1
                  /* TEXT */
                )) : vue.createCommentVNode("v-if", true),
                vue.createElementVNode("view", { class: "meta" }, [
                  vue.createElementVNode(
                    "text",
                    { class: "price" },
                    "¥" + vue.toDisplayString($options.formatPrice(it.price)),
                    1
                    /* TEXT */
                  ),
                  vue.createElementVNode(
                    "text",
                    { class: "qty" },
                    "×" + vue.toDisplayString(it.quantity),
                    1
                    /* TEXT */
                  )
                ])
              ])
            ]);
          }),
          128
          /* KEYED_FRAGMENT */
        ))
      ])
    ]);
  }
  const PagesOrderDetailOrderDetail = /* @__PURE__ */ _export_sfc(_sfc_main$5, [["render", _sfc_render$4], ["__scopeId", "data-v-71729483"], ["__file", "/Users/chenjianping/Desktop/private/pro/sheng/yinjiajia/app/front-app-uni/pages/order-detail/order-detail.vue"]]);
  const _sfc_main$4 = {
    data() {
      return {
        paymentStatus: "success",
        // success 或 fail
        orderInfo: {
          orderNo: "",
          totalAmount: "0.00",
          payTime: ""
        }
      };
    },
    mounted() {
      this.loadPaymentResult();
    },
    methods: {
      // 加载支付结果
      loadPaymentResult() {
        const pages = getCurrentPages();
        const currentPage = pages[pages.length - 1];
        const options = currentPage.options;
        this.paymentStatus = options.status || "success";
        this.orderInfo.orderNo = options.order_number || "";
        this.orderInfo.totalAmount = options.total_amount || "0.00";
        this.orderInfo.payTime = this.formatDate(/* @__PURE__ */ new Date());
      },
      // 格式化日期
      formatDate(date) {
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, "0");
        const day = date.getDate().toString().padStart(2, "0");
        const hours = date.getHours().toString().padStart(2, "0");
        const minutes = date.getMinutes().toString().padStart(2, "0");
        const seconds = date.getSeconds().toString().padStart(2, "0");
        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
      },
      // 返回上一页
      goBack() {
        uni.navigateBack({
          delta: 1
        });
      },
      // 查看订单
      viewOrder() {
        uni.navigateTo({
          url: "/pages/myorder/myorder"
        });
      },
      // 重新支付
      retryPayment() {
        uni.navigateTo({
          url: "/pages/payment/payment?order_number=" + this.orderInfo.orderNo + "&total_amount=" + this.orderInfo.totalAmount
        });
      },
      // 返回首页
      goHome() {
        uni.switchTab({
          url: "/pages/index/index"
        });
      }
    }
  };
  function _sfc_render$3(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "pay-result-container" }, [
      vue.createCommentVNode(" 头部 "),
      vue.createElementVNode("view", { class: "header" }, [
        vue.createElementVNode("view", {
          class: "back-btn",
          onClick: _cache[0] || (_cache[0] = (...args) => $options.goBack && $options.goBack(...args))
        }, [
          vue.createElementVNode("text", null, "←")
        ]),
        vue.createElementVNode("view", { class: "title" }, "支付结果")
      ]),
      vue.createCommentVNode(" 支付结果内容 "),
      vue.createElementVNode("view", { class: "result-content" }, [
        vue.createCommentVNode(" 成功状态 "),
        $data.paymentStatus === "success" ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 0,
          class: "success-result"
        }, [
          vue.createElementVNode("view", { class: "result-icon success" }, [
            vue.createElementVNode("text", null, "✓")
          ]),
          vue.createElementVNode("view", { class: "result-title" }, "支付成功"),
          vue.createElementVNode("view", { class: "result-desc" }, "您的订单已支付成功，我们会尽快为您发货"),
          vue.createElementVNode("view", { class: "order-info" }, [
            vue.createElementVNode("view", { class: "info-item" }, [
              vue.createElementVNode("text", { class: "label" }, "订单号："),
              vue.createElementVNode(
                "text",
                { class: "value" },
                vue.toDisplayString($data.orderInfo.orderNo),
                1
                /* TEXT */
              )
            ]),
            vue.createElementVNode("view", { class: "info-item" }, [
              vue.createElementVNode("text", { class: "label" }, "支付金额："),
              vue.createElementVNode(
                "text",
                { class: "value price" },
                "¥" + vue.toDisplayString($data.orderInfo.totalAmount),
                1
                /* TEXT */
              )
            ]),
            vue.createElementVNode("view", { class: "info-item" }, [
              vue.createElementVNode("text", { class: "label" }, "支付时间："),
              vue.createElementVNode(
                "text",
                { class: "value" },
                vue.toDisplayString($data.orderInfo.payTime),
                1
                /* TEXT */
              )
            ])
          ])
        ])) : (vue.openBlock(), vue.createElementBlock(
          vue.Fragment,
          { key: 1 },
          [
            vue.createCommentVNode(" 失败状态 "),
            vue.createElementVNode("view", { class: "fail-result" }, [
              vue.createElementVNode("view", { class: "result-icon fail" }, [
                vue.createElementVNode("text", null, "✗")
              ]),
              vue.createElementVNode("view", { class: "result-title" }, "支付失败"),
              vue.createElementVNode("view", { class: "result-desc" }, "支付过程中出现问题，请重新尝试"),
              vue.createElementVNode("view", { class: "order-info" }, [
                vue.createElementVNode("view", { class: "info-item" }, [
                  vue.createElementVNode("text", { class: "label" }, "订单号："),
                  vue.createElementVNode(
                    "text",
                    { class: "value" },
                    vue.toDisplayString($data.orderInfo.orderNo),
                    1
                    /* TEXT */
                  )
                ]),
                vue.createElementVNode("view", { class: "info-item" }, [
                  vue.createElementVNode("text", { class: "label" }, "应付金额："),
                  vue.createElementVNode(
                    "text",
                    { class: "value price" },
                    "¥" + vue.toDisplayString($data.orderInfo.totalAmount),
                    1
                    /* TEXT */
                  )
                ])
              ])
            ])
          ],
          2112
          /* STABLE_FRAGMENT, DEV_ROOT_FRAGMENT */
        ))
      ]),
      vue.createCommentVNode(" 操作按钮 "),
      vue.createElementVNode("view", { class: "action-buttons" }, [
        $data.paymentStatus === "success" ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 0,
          class: "btn-group"
        }, [
          vue.createElementVNode("button", {
            class: "btn btn-secondary",
            onClick: _cache[1] || (_cache[1] = (...args) => $options.viewOrder && $options.viewOrder(...args))
          }, "查看订单"),
          vue.createElementVNode("button", {
            class: "btn btn-primary",
            onClick: _cache[2] || (_cache[2] = (...args) => $options.goHome && $options.goHome(...args))
          }, "返回首页")
        ])) : (vue.openBlock(), vue.createElementBlock("view", {
          key: 1,
          class: "btn-group"
        }, [
          vue.createElementVNode("button", {
            class: "btn btn-secondary",
            onClick: _cache[3] || (_cache[3] = (...args) => $options.retryPayment && $options.retryPayment(...args))
          }, "重新支付"),
          vue.createElementVNode("button", {
            class: "btn btn-primary",
            onClick: _cache[4] || (_cache[4] = (...args) => $options.goHome && $options.goHome(...args))
          }, "返回首页")
        ]))
      ])
    ]);
  }
  const PagesPayResultPayResult = /* @__PURE__ */ _export_sfc(_sfc_main$4, [["render", _sfc_render$3], ["__scopeId", "data-v-82869e9d"], ["__file", "/Users/chenjianping/Desktop/private/pro/sheng/yinjiajia/app/front-app-uni/pages/pay-result/pay-result.vue"]]);
  const _sfc_main$3 = {
    name: "CustomTabbar",
    props: {
      selected: {
        type: Number,
        default: 0
      }
    },
    data() {
      return {
        cartCount: 0,
        userId: getUserId()
      };
    },
    methods: {
      navigateTo(path) {
        if (path === "/") {
          uni.switchTab({
            url: "/pages/index/index"
          });
        } else if (path === "/cart") {
          uni.switchTab({
            url: "/pages/cart/cart"
          });
        } else if (path === "/myorder") {
          uni.switchTab({
            url: "/pages/myorder/myorder"
          });
        } else if (path === "/profile") {
          uni.switchTab({
            url: "/pages/profile/profile"
          });
        } else {
          uni.navigateTo({
            url: path
          });
        }
      },
      async fetchCartCount() {
        var _a;
        const pages = getCurrentPages();
        const currentPage = pages[pages.length - 1];
        if (currentPage && currentPage.route === "pages/cart/cart")
          return;
        const uid = getUserId();
        if (!uid) {
          this.cartCount = 0;
          return;
        }
        try {
          const response = await cartApi.getCart(uid);
          if (response.data && response.data.code === 200) {
            const count = ((_a = response.data.data) == null ? void 0 : _a.item_count) ?? 0;
            this.cartCount = Number.isFinite(count) ? count : 0;
          }
        } catch (e) {
        }
      }
    },
    onShow() {
      this.fetchCartCount();
    },
    onHide() {
    }
  };
  function _sfc_render$2(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "custom-tabbar" }, [
      vue.createElementVNode(
        "view",
        {
          class: vue.normalizeClass(["tabbar-item", { active: $props.selected === 0 }]),
          onClick: _cache[0] || (_cache[0] = ($event) => $options.navigateTo("/"))
        },
        [
          vue.createElementVNode("view", { class: "icon" }, "🏪"),
          vue.createElementVNode("view", { class: "label" }, "商城")
        ],
        2
        /* CLASS */
      ),
      vue.createElementVNode(
        "view",
        {
          class: vue.normalizeClass(["tabbar-item", { active: $props.selected === 1 }]),
          onClick: _cache[1] || (_cache[1] = ($event) => $options.navigateTo("/cart"))
        },
        [
          vue.createElementVNode("view", { class: "icon" }, [
            vue.createTextVNode(" 🛒 "),
            $data.cartCount > 0 ? (vue.openBlock(), vue.createElementBlock(
              "text",
              {
                key: 0,
                class: "badge"
              },
              vue.toDisplayString($data.cartCount > 99 ? "99+" : $data.cartCount),
              1
              /* TEXT */
            )) : vue.createCommentVNode("v-if", true)
          ]),
          vue.createElementVNode("view", { class: "label" }, "购物车")
        ],
        2
        /* CLASS */
      ),
      vue.createElementVNode(
        "view",
        {
          class: vue.normalizeClass(["tabbar-item", { active: $props.selected === 2 }]),
          onClick: _cache[2] || (_cache[2] = ($event) => $options.navigateTo("/profile"))
        },
        [
          vue.createElementVNode("view", { class: "icon" }, "👤"),
          vue.createElementVNode("view", { class: "label" }, "我的")
        ],
        2
        /* CLASS */
      ),
      vue.createElementVNode(
        "view",
        {
          class: vue.normalizeClass(["tabbar-item", { active: $props.selected === 3 }]),
          onClick: _cache[3] || (_cache[3] = ($event) => $options.navigateTo("/customer-service"))
        },
        [
          vue.createElementVNode("view", { class: "icon" }, "💬"),
          vue.createElementVNode("view", { class: "label" }, "客服")
        ],
        2
        /* CLASS */
      )
    ]);
  }
  const customTabbar = /* @__PURE__ */ _export_sfc(_sfc_main$3, [["render", _sfc_render$2], ["__scopeId", "data-v-66a838af"], ["__file", "/Users/chenjianping/Desktop/private/pro/sheng/yinjiajia/app/front-app-uni/src/components/custom-tabbar/custom-tabbar.vue"]]);
  const _sfc_main$2 = {
    components: {
      customTabbar
    },
    data() {
      return {
        selectedTabIndex: 1,
        activeCategory: 0,
        // 添加模拟分类数据
        groups: [
          {
            id: 1,
            name: "推荐"
          },
          {
            id: 2,
            name: "手机数码"
          },
          {
            id: 3,
            name: "家用电器"
          },
          {
            id: 4,
            name: "食品生鲜"
          },
          {
            id: 5,
            name: "美妆护肤"
          },
          {
            id: 6,
            name: "服饰鞋包"
          },
          {
            id: 7,
            name: "家居生活"
          }
        ],
        products: [],
        page: 1,
        pageSize: 10,
        loading: false,
        noMore: false,
        cartCount: 3,
        // 设置默认购物车数量
        columnHeights: {
          left: 0,
          right: 0
        }
      };
    },
    computed: {
      leftColumnItems() {
        return this.products.filter((item) => item.column === "left");
      },
      rightColumnItems() {
        return this.products.filter((item) => item.column === "right");
      }
    },
    methods: {
      distributeProducts(newProducts) {
        newProducts.forEach((item) => {
          const itemHeight = Math.random() * 100 + 200;
          if (this.columnHeights.left <= this.columnHeights.right) {
            item.column = "left";
            this.columnHeights.left += itemHeight;
          } else {
            item.column = "right";
            this.columnHeights.right += itemHeight;
          }
        });
      },
      async fetchCategories() {
        try {
          this.fetchProducts(this.groups[0].id);
        } catch (error) {
          formatAppLog("error", "at pages/purchase/purchase.vue:162", "获取分类失败:", error);
        }
      },
      async fetchProducts(categoryId, isLoadMore = false) {
        if (this.loading)
          return;
        this.loading = true;
        if (!isLoadMore) {
          this.page = 1;
          this.noMore = false;
          this.columnHeights = {
            left: 0,
            right: 0
          };
        }
        try {
          const mockProducts = this.generateMockProducts(categoryId);
          const newProducts = mockProducts.data.items;
          this.distributeProducts(newProducts);
          if (isLoadMore) {
            this.products = [...this.products, ...newProducts];
          } else {
            this.products = newProducts;
          }
          if (newProducts.length < this.pageSize) {
            this.noMore = true;
          }
          this.page++;
        } catch (error) {
          formatAppLog("error", "at pages/purchase/purchase.vue:207", "获取商品失败:", error);
        } finally {
          this.loading = false;
        }
      },
      // 添加生成模拟商品数据的方法
      generateMockProducts(categoryId) {
        const categoryMap = {
          1: ["推荐商品", "red"],
          2: ["手机", "digital"],
          3: ["家电", "appliance"],
          4: ["食品", "food"],
          5: ["美妆", "beauty"],
          6: ["服饰", "clothing"],
          7: ["家居", "home"]
        };
        const [categoryName, type] = categoryMap[categoryId] || ["商品", "product"];
        const mockImages = [
          "https://img.yzcdn.cn/vant/apple-1.jpg",
          "https://img.yzcdn.cn/vant/apple-2.jpg",
          "https://img.yzcdn.cn/vant/apple-3.jpg",
          "https://img.yzcdn.cn/vant/apple-4.jpg",
          "https://img.yzcdn.cn/vant/apple-5.jpg",
          "https://img.yzcdn.cn/vant/apple-6.jpg",
          "https://img.yzcdn.cn/vant/apple-7.jpg",
          "https://img.yzcdn.cn/vant/apple-8.jpg"
        ];
        const products = [];
        for (let i = 0; i < this.pageSize; i++) {
          const price = (Math.random() * 100 + 20).toFixed(2);
          const originalPrice = (parseFloat(price) + Math.random() * 50).toFixed(2);
          products.push({
            id: `${categoryId}_${this.page}_${i}`,
            title: `${categoryName}${i + 1} ${this.getRandomProductDesc(type)}`,
            price,
            original_price: Math.random() > 0.3 ? originalPrice : null,
            sales: Math.floor(Math.random() * 1e3),
            image: mockImages[i % mockImages.length]
          });
        }
        return {
          code: 200,
          data: {
            items: products
          }
        };
      },
      // 添加获取随机商品描述的方法
      getRandomProductDesc(type) {
        const descMap = {
          red: ["新品上市", "热卖推荐", "限时特惠", "爆款"],
          digital: ["智能手机", "蓝牙耳机", "智能手表", "平板电脑", "数码相机"],
          appliance: ["冰箱", "洗衣机", "空调", "电视机", "微波炉"],
          food: ["新鲜水果", "进口零食", "有机蔬菜", "海鲜水产"],
          beauty: ["精华液", "面膜", "口红", "粉底液", "眼霜"],
          clothing: ["T恤", "牛仔裤", "连衣裙", "运动鞋", "外套"],
          home: ["床上用品", "厨具", "收纳", "装饰画", "灯具"],
          product: ["优质商品", "热销商品", "新品", "特价商品"]
        };
        const descs = descMap[type] || descMap.product;
        return descs[Math.floor(Math.random() * descs.length)];
      },
      changeCategory(index) {
        this.activeCategory = index;
        const categoryId = this.groups[index].id;
        this.fetchProducts(categoryId);
      },
      goToDetail(productId) {
        uni.navigateTo({
          url: `/pages/trade-list/product-detail?id=${productId}`
        });
      },
      goToSearch() {
        uni.navigateTo({
          url: "/pages/search/products"
        });
      },
      goToCart() {
        uni.navigateTo({
          url: "/pages/trade-list/cartList"
        });
      },
      async fetchCartCount() {
        try {
          this.cartCount = Math.floor(Math.random() * 10);
        } catch (error) {
          formatAppLog("error", "at pages/purchase/purchase.vue:311", "获取购物车数量失败:", error);
        }
      },
      onReachBottomHandler() {
        if (!this.noMore && !this.loading) {
          const categoryId = this.groups[this.activeCategory].id;
          this.fetchProducts(categoryId, true);
        }
      }
    },
    mounted() {
      this.fetchCategories();
      this.fetchCartCount();
    },
    onReachBottom() {
      this.onReachBottomHandler();
    }
  };
  function _sfc_render$1(_ctx, _cache, $props, $setup, $data, $options) {
    const _component_uni_icons = vue.resolveComponent("uni-icons");
    const _component_custom_tabbar = vue.resolveComponent("custom-tabbar");
    return vue.openBlock(), vue.createElementBlock(
      vue.Fragment,
      null,
      [
        vue.createElementVNode("view", { class: "uni-status-bar" }),
        vue.createElementVNode("view", { class: "shop-container" }, [
          vue.createCommentVNode(" 顶部搜索栏和购物车 "),
          vue.createElementVNode("view", { class: "top-bar" }, [
            vue.createElementVNode("view", {
              class: "search-bar",
              onClick: _cache[0] || (_cache[0] = (...args) => $options.goToSearch && $options.goToSearch(...args))
            }, [
              vue.createVNode(_component_uni_icons, {
                type: "search",
                size: "18",
                color: "#999"
              }),
              vue.createElementVNode("text", { class: "search-text" }, "搜索商品111")
            ]),
            vue.createElementVNode("view", {
              class: "cart-icon",
              onClick: _cache[1] || (_cache[1] = (...args) => $options.goToCart && $options.goToCart(...args))
            }, [
              vue.createVNode(_component_uni_icons, {
                type: "cart",
                size: "24",
                color: "#ff2442"
              }),
              $data.cartCount > 0 ? (vue.openBlock(), vue.createElementBlock(
                "text",
                {
                  key: 0,
                  class: "cart-badge"
                },
                vue.toDisplayString($data.cartCount),
                1
                /* TEXT */
              )) : vue.createCommentVNode("v-if", true)
            ])
          ]),
          vue.createCommentVNode(" 分类标签栏 "),
          vue.createElementVNode("scroll-view", {
            class: "group-tabs",
            "scroll-x": ""
          }, [
            (vue.openBlock(true), vue.createElementBlock(
              vue.Fragment,
              null,
              vue.renderList($data.groups, (group, index) => {
                return vue.openBlock(), vue.createElementBlock("view", {
                  key: group.id,
                  class: vue.normalizeClass(["tab-item", { active: $data.activeCategory === index }]),
                  onClick: ($event) => $options.changeCategory(index)
                }, vue.toDisplayString(group.name), 11, ["onClick"]);
              }),
              128
              /* KEYED_FRAGMENT */
            ))
          ]),
          vue.createCommentVNode(" 商品瀑布流 "),
          vue.createElementVNode("view", { class: "waterfall-container" }, [
            vue.createElementVNode("view", { class: "waterfall-column" }, [
              (vue.openBlock(true), vue.createElementBlock(
                vue.Fragment,
                null,
                vue.renderList($options.leftColumnItems, (item, index) => {
                  return vue.openBlock(), vue.createElementBlock("view", {
                    key: item.id,
                    class: "product-item",
                    onClick: ($event) => $options.goToDetail(item.id)
                  }, [
                    vue.createElementVNode("image", {
                      class: "product-image",
                      src: item.image,
                      mode: "widthFix"
                    }, null, 8, ["src"]),
                    vue.createElementVNode("view", { class: "product-info" }, [
                      vue.createElementVNode(
                        "text",
                        { class: "product-title" },
                        vue.toDisplayString(item.title),
                        1
                        /* TEXT */
                      ),
                      vue.createElementVNode("view", { class: "price-section" }, [
                        vue.createElementVNode(
                          "text",
                          { class: "product-price" },
                          "¥" + vue.toDisplayString(item.price),
                          1
                          /* TEXT */
                        ),
                        item.original_price ? (vue.openBlock(), vue.createElementBlock(
                          "text",
                          {
                            key: 0,
                            class: "original-price"
                          },
                          "¥" + vue.toDisplayString(item.original_price),
                          1
                          /* TEXT */
                        )) : vue.createCommentVNode("v-if", true)
                      ]),
                      vue.createElementVNode("view", { class: "sales-info" }, [
                        vue.createElementVNode(
                          "text",
                          null,
                          "已售" + vue.toDisplayString(item.sales) + "件",
                          1
                          /* TEXT */
                        )
                      ])
                    ])
                  ], 8, ["onClick"]);
                }),
                128
                /* KEYED_FRAGMENT */
              ))
            ]),
            vue.createElementVNode("view", { class: "waterfall-column" }, [
              (vue.openBlock(true), vue.createElementBlock(
                vue.Fragment,
                null,
                vue.renderList($options.rightColumnItems, (item, index) => {
                  return vue.openBlock(), vue.createElementBlock("view", {
                    key: item.id,
                    class: "product-item",
                    onClick: ($event) => $options.goToDetail(item.id)
                  }, [
                    vue.createElementVNode("image", {
                      class: "product-image",
                      src: item.image,
                      mode: "widthFix"
                    }, null, 8, ["src"]),
                    vue.createElementVNode("view", { class: "product-info" }, [
                      vue.createElementVNode(
                        "text",
                        { class: "product-title" },
                        vue.toDisplayString(item.title),
                        1
                        /* TEXT */
                      ),
                      vue.createElementVNode("view", { class: "price-section" }, [
                        vue.createElementVNode(
                          "text",
                          { class: "product-price" },
                          "¥" + vue.toDisplayString(item.price),
                          1
                          /* TEXT */
                        ),
                        item.original_price ? (vue.openBlock(), vue.createElementBlock(
                          "text",
                          {
                            key: 0,
                            class: "original-price"
                          },
                          "¥" + vue.toDisplayString(item.original_price),
                          1
                          /* TEXT */
                        )) : vue.createCommentVNode("v-if", true)
                      ]),
                      vue.createElementVNode("view", { class: "sales-info" }, [
                        vue.createElementVNode(
                          "text",
                          null,
                          "已售" + vue.toDisplayString(item.sales) + "件",
                          1
                          /* TEXT */
                        )
                      ])
                    ])
                  ], 8, ["onClick"]);
                }),
                128
                /* KEYED_FRAGMENT */
              ))
            ])
          ]),
          vue.createCommentVNode(" 加载更多提示 "),
          $data.loading ? (vue.openBlock(), vue.createElementBlock("view", {
            key: 0,
            class: "load-more"
          }, [
            vue.createElementVNode("text", null, "加载中...")
          ])) : $data.noMore ? (vue.openBlock(), vue.createElementBlock("view", {
            key: 1,
            class: "load-more"
          }, [
            vue.createElementVNode("text", null, "没有更多了~")
          ])) : vue.createCommentVNode("v-if", true),
          vue.createVNode(_component_custom_tabbar, { selected: $data.selectedTabIndex }, null, 8, ["selected"])
        ])
      ],
      64
      /* STABLE_FRAGMENT */
    );
  }
  const PagesPurchasePurchase = /* @__PURE__ */ _export_sfc(_sfc_main$2, [["render", _sfc_render$1], ["__scopeId", "data-v-313e55f0"], ["__file", "/Users/chenjianping/Desktop/private/pro/sheng/yinjiajia/app/front-app-uni/pages/purchase/purchase.vue"]]);
  const _sfc_main$1 = {
    name: "PaymentMethod",
    data() {
      return {
        orderType: "direct",
        // 'cart' 或 'direct'
        totalAmount: "0.00",
        quantity: 1,
        cartItemCount: 0,
        selectedMethod: "wechat",
        pageOptions: {},
        // 页面参数
        paymentMethods: [
          {
            id: "wechat",
            name: "微信支付",
            description: "推荐使用微信支付",
            icon: "wechat-icon"
          },
          {
            id: "alipay",
            name: "支付宝",
            description: "安全便捷的支付方式",
            icon: "alipay-icon"
          }
        ]
      };
    },
    onLoad(options) {
      this.pageOptions = options;
      this.loadOrderInfo();
    },
    methods: {
      goBack() {
        uni.navigateBack({
          delta: 1
        });
      },
      loadOrderInfo() {
        const query = this.pageOptions;
        if (query.cart_items) {
          this.orderType = "cart";
          this.cartItemCount = query.cart_items.split(",").length;
        } else {
          this.orderType = "direct";
          this.quantity = parseInt(query.quantity) || 1;
        }
        this.totalAmount = query.total_amount || "0.00";
      },
      selectMethod(methodId) {
        this.selectedMethod = methodId;
      },
      async confirmPayment() {
        if (!this.selectedMethod) {
          uni.showToast({
            title: "请选择支付方式",
            icon: "error"
          });
          return;
        }
        try {
          const query = this.pageOptions;
          let addressId = parseInt(query.address_id) || 1;
          if (!query.address_id) {
            try {
              const addressResponse = await request$1.get("/api/app/address/default", {
                params: { user_id: getUserId() }
              });
              if (addressResponse.data.code === 200 && addressResponse.data.data) {
                addressId = addressResponse.data.data.id;
              }
            } catch (error) {
              formatAppLog("warn", "at pages/payment-method/payment-method.vue:155", "获取默认地址失败，使用默认值:", error);
            }
          }
          const orderData = {
            user_id: getUserId(),
            payment_method: this.selectedMethod,
            address_id: addressId
          };
          if (this.orderType === "cart") {
            orderData.cart_items = query.cart_items.split(",").map((id) => parseInt(id));
          } else {
            orderData.direct_buy = {
              product_id: parseInt(query.product_id),
              quantity: parseInt(query.quantity)
            };
            if (query.spec_combination_id) {
              orderData.direct_buy.spec_combination_id = parseInt(query.spec_combination_id);
            }
          }
          formatAppLog("log", "at pages/payment-method/payment-method.vue:179", "创建订单数据:", orderData);
          const response = await request$1.post("/api/app/order/", orderData);
          if (response.data.code === 200) {
            formatAppLog("log", "at pages/payment-method/payment-method.vue:183", "订单创建成功:", response.data);
            uni.navigateTo({
              url: `/pages/payment/payment?order_id=${response.data.data.order_id}&order_number=${response.data.data.order_number}&total_amount=${response.data.data.total_amount}&payment_method=${this.selectedMethod}`
            });
          } else {
            formatAppLog("error", "at pages/payment-method/payment-method.vue:189", "创建订单失败:", response.data);
            uni.showToast({
              title: response.data.message || "创建订单失败",
              icon: "error"
            });
          }
        } catch (error) {
          formatAppLog("error", "at pages/payment-method/payment-method.vue:196", "创建订单失败:", error);
          uni.showToast({
            title: "创建订单失败，请重试",
            icon: "error"
          });
        }
      }
    }
  };
  function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
    return vue.openBlock(), vue.createElementBlock("view", { class: "payment-method-container" }, [
      vue.createCommentVNode(" 头部 "),
      vue.createElementVNode("view", { class: "header" }, [
        vue.createElementVNode("view", {
          class: "back-btn",
          onClick: _cache[0] || (_cache[0] = (...args) => $options.goBack && $options.goBack(...args))
        }, [
          vue.createElementVNode("text", null, "←")
        ]),
        vue.createElementVNode("view", { class: "title" }, "选择支付方式")
      ]),
      vue.createCommentVNode(" 订单信息 "),
      vue.createElementVNode("view", { class: "order-info" }, [
        vue.createElementVNode("view", { class: "info-item" }, [
          vue.createElementVNode("text", { class: "label" }, "订单金额"),
          vue.createElementVNode(
            "text",
            { class: "value price" },
            "¥" + vue.toDisplayString($data.totalAmount),
            1
            /* TEXT */
          )
        ]),
        $data.orderType === "direct" ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 0,
          class: "info-item"
        }, [
          vue.createElementVNode("text", { class: "label" }, "商品数量"),
          vue.createElementVNode(
            "text",
            { class: "value" },
            vue.toDisplayString($data.quantity) + "件",
            1
            /* TEXT */
          )
        ])) : vue.createCommentVNode("v-if", true),
        $data.orderType === "cart" ? (vue.openBlock(), vue.createElementBlock("view", {
          key: 1,
          class: "info-item"
        }, [
          vue.createElementVNode("text", { class: "label" }, "商品数量"),
          vue.createElementVNode(
            "text",
            { class: "value" },
            vue.toDisplayString($data.cartItemCount) + "件",
            1
            /* TEXT */
          )
        ])) : vue.createCommentVNode("v-if", true)
      ]),
      vue.createCommentVNode(" 支付方式列表 "),
      vue.createElementVNode("view", { class: "payment-methods" }, [
        vue.createElementVNode("view", { class: "section-title" }, "选择支付方式"),
        vue.createElementVNode("view", { class: "method-list" }, [
          (vue.openBlock(true), vue.createElementBlock(
            vue.Fragment,
            null,
            vue.renderList($data.paymentMethods, (method) => {
              return vue.openBlock(), vue.createElementBlock("view", {
                class: vue.normalizeClass(["method-item", { selected: $data.selectedMethod === method.id }]),
                key: method.id,
                onClick: ($event) => $options.selectMethod(method.id)
              }, [
                vue.createElementVNode("view", { class: "method-left" }, [
                  vue.createElementVNode("view", { class: "method-icon" }, [
                    vue.createElementVNode(
                      "text",
                      {
                        class: vue.normalizeClass(method.icon)
                      },
                      null,
                      2
                      /* CLASS */
                    )
                  ]),
                  vue.createElementVNode("view", { class: "method-info" }, [
                    vue.createElementVNode(
                      "view",
                      { class: "method-name" },
                      vue.toDisplayString(method.name),
                      1
                      /* TEXT */
                    ),
                    vue.createElementVNode(
                      "view",
                      { class: "method-desc" },
                      vue.toDisplayString(method.description),
                      1
                      /* TEXT */
                    )
                  ])
                ]),
                vue.createElementVNode("view", { class: "method-right" }, [
                  vue.createElementVNode(
                    "view",
                    {
                      class: vue.normalizeClass(["radio-btn", { active: $data.selectedMethod === method.id }])
                    },
                    [
                      vue.createElementVNode("text", { class: "radio-inner" })
                    ],
                    2
                    /* CLASS */
                  )
                ])
              ], 10, ["onClick"]);
            }),
            128
            /* KEYED_FRAGMENT */
          ))
        ])
      ]),
      vue.createCommentVNode(" 底部确认按钮 "),
      vue.createElementVNode("view", { class: "bottom-bar" }, [
        vue.createElementVNode("view", { class: "total-info" }, [
          vue.createElementVNode("text", null, "应付金额："),
          vue.createElementVNode(
            "text",
            { class: "total-price" },
            "¥" + vue.toDisplayString($data.totalAmount),
            1
            /* TEXT */
          )
        ]),
        vue.createElementVNode(
          "view",
          {
            class: vue.normalizeClass(["confirm-btn", { disabled: !$data.selectedMethod }]),
            onClick: _cache[1] || (_cache[1] = (...args) => $options.confirmPayment && $options.confirmPayment(...args))
          },
          " 确认支付 ",
          2
          /* CLASS */
        )
      ])
    ]);
  }
  const PagesPaymentMethodPaymentMethod = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["render", _sfc_render], ["__scopeId", "data-v-01a39e44"], ["__file", "/Users/chenjianping/Desktop/private/pro/sheng/yinjiajia/app/front-app-uni/pages/payment-method/payment-method.vue"]]);
  __definePage("pages/shop/shop", PagesShopShop);
  __definePage("pages/cart/cart", PagesCartCart);
  __definePage("pages/profile/profile", PagesProfileProfile);
  __definePage("pages/customer-service/customer-service", PagesCustomerServiceCustomerService);
  __definePage("pages/product-detail/product-detail", PagesProductDetailProductDetail);
  __definePage("pages/checkout/checkout", PagesCheckoutCheckout);
  __definePage("pages/payment/payment", PagesPaymentPayment);
  __definePage("pages/login/login", PagesLoginLogin);
  __definePage("pages/register/register", PagesRegisterRegister);
  __definePage("pages/myorder/myorder", PagesMyorderMyorder);
  __definePage("pages/address/address", PagesAddressAddress);
  __definePage("pages/address-list/address-list", PagesAddressListAddressList);
  __definePage("pages/order-detail/order-detail", PagesOrderDetailOrderDetail);
  __definePage("pages/pay-result/pay-result", PagesPayResultPayResult);
  __definePage("pages/purchase/purchase", PagesPurchasePurchase);
  __definePage("pages/payment-method/payment-method", PagesPaymentMethodPaymentMethod);
  const _sfc_main = {
    onLaunch: function() {
      formatAppLog("log", "at App.vue:4", "App Launch");
    },
    onShow: function() {
      formatAppLog("log", "at App.vue:8", "App Show");
    },
    onHide: function() {
      formatAppLog("log", "at App.vue:12", "App Hide");
    }
  };
  const App = /* @__PURE__ */ _export_sfc(_sfc_main, [["__file", "/Users/chenjianping/Desktop/private/pro/sheng/yinjiajia/app/front-app-uni/App.vue"]]);
  function createApp() {
    const app = vue.createVueApp(App);
    return {
      app
    };
  }
  const { app: __app__, Vuex: __Vuex__, Pinia: __Pinia__ } = createApp();
  uni.Vuex = __Vuex__;
  uni.Pinia = __Pinia__;
  __app__.provide("__globalStyles", __uniConfig.styles);
  __app__._component.mpType = "app";
  __app__._component.render = () => {
  };
  __app__.mount("#app");
})(Vue);
