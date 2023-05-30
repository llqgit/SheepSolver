#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create Time: 2023/05/25 00:00
# Create User: NB-Dragon
from core.card.CardContainer import CardContainer
from core.pool.OperationPool import OperationPool
from core.pool.ResidualPool import ResidualPool


class GamePoolController(object):
    def __init__(self, solve_type, global_config):
        self._solve_type = solve_type
        self._global_config = global_config
        self._card_container = CardContainer()
        self._operation_pool = OperationPool(self._card_container)
        self._residual_pool = ResidualPool(self._card_container)

    def init_map_data(self, map_data):
        level_key_list = list(sorted(map_data["levelData"].keys(), key=lambda item: int(item)))
        for level_key in level_key_list:
            level_data = map_data["levelData"][level_key]
            self._card_container.append_level_card(level_data)

    def prepare_game_data(self):
        self._operation_pool.prepare_game_data()
        self._residual_pool.prepare_game_data()

    def export_game_data(self):
        card = self._card_container.export_compute_data_string()
        return {"card": card}

    def import_game_data(self, game_data):
        card = game_data["card"]
        self._card_container.import_compute_data_string(card)

    def get_all_card_count(self):
        return self._card_container.get_card_count()

    def get_all_card_dict(self):
        card_range = range(self._card_container.get_card_count())
        return self._card_container.get_card_detail_dict(card_range)

    def is_game_over(self):
        main_zone_card_list = self._operation_pool.get_main_zone_show_card_list(self._solve_type)
        return len(main_zone_card_list) == 0

    def generate_head_list(self):
        main_zone_card_list = self._operation_pool.get_main_zone_show_card_list(self._solve_type)
        return main_zone_card_list

    def generate_head_fingerprint(self):
        main_zone_card_list = self._operation_pool.get_main_zone_show_card_list(self._solve_type)
        all_key_list = list(sorted(main_zone_card_list))
        return "-".join([str(item) for item in all_key_list])

    def ensure_head_list_alive(self, index_list):
        expect_card_dict = self._card_container.get_card_detail_dict(index_list)
        card_type_dict = {index: card_detail.get_card_type() for index, card_detail in expect_card_dict.items()}
        if self._residual_pool.is_card_type_close_to_limit():
            return []
        elif self._residual_pool.is_pool_count_close_to_limit():
            expect_type_list = self._residual_pool.get_almost_card_type_list()
            return self._find_match_type_list(card_type_dict.items(), expect_type_list)
        elif self._residual_pool.is_card_type_close_to_possible():
            expect_type_list = self._residual_pool.get_all_card_type_list()
            return self._find_match_type_list(card_type_dict.items(), expect_type_list)
        else:
            return index_list

    def ensure_head_list_disappear(self, index_list, progress):
        expect_card_dict = self._card_container.get_card_detail_dict(index_list)
        card_type_dict = {index: card_detail.get_card_type() for index, card_detail in expect_card_dict.items()}
        if progress >= self._global_config["solve_first"]:
            expect_type_list = self._residual_pool.get_sorted_card_type_list()
            return self._sort_head_list_with_type_list(card_type_dict, expect_type_list)
        else:
            return index_list

    def pick_card(self, card_index):
        self._operation_pool.pick_card(card_index)
        self._residual_pool.pick_card(card_index)

    def recover_card(self, card_index):
        self._operation_pool.recover_card(card_index)
        self._residual_pool.recover_card(card_index)

    def _sort_head_list_with_type_list(self, card_type_dict, card_type_list):
        result_list = list()
        for type_item in card_type_list:
            match_list = self._find_match_type_list(card_type_dict.items(), [type_item])
            result_list.extend(match_list)
        last_index_list = [index for index in card_type_dict.keys() if index not in result_list]
        return result_list + last_index_list

    @staticmethod
    def _find_match_type_list(enumerable_data, expect_type_list):
        return [index for index, card_type in enumerable_data if card_type in expect_type_list]
