import sys
from collections import defaultdict
import math
import copy


class Apriori:
    def __init__(self, min_support, input_file, output_file):
        data = []
        with open(input_file, 'r') as f:
            for line in f.readlines():
                line = [int(c) for c in line.split('\t')]
                data.append(sorted(line))
        total_num = len(data)

        self.fp = []
        self.ars = []
        self.sup_mat = []
        self.min_support_num = math.ceil(total_num*min_support/100)
        self.total_num = total_num

        def initialize(data):
            d = defaultdict(lambda: 0)
            L1_list = []
            L0_set = set()
            L1_sup_list = []
            for itemset in data:
                for item in itemset:
                    d[item] += 1
            for item, sup in d.items():
                if sup >= self.min_support_num:
                    L1_list.append([item])
                    L1_sup_list.append(sup*100/self.total_num)
                else:
                    L0_set.add(item)
            new_data = []
            for n, itemset in enumerate(data):
                itemset = list(set(itemset)-L0_set)
                if len(itemset) != 0:
                    new_data.append(itemset)
            return new_data, L1_list, L1_sup_list

        self.data, l1_list, sup_list = initialize(data)
        self.fp.append(l1_list)
        self.sup_mat.append(sup_list)
        self.output_file = output_file

    def all_frequent_patterns(self):
        def generate_candidates(k_fp_list, k):
            candidate_list = []
            k_fp_list_cp = copy.deepcopy(k_fp_list)
            for i, itemset in enumerate(k_fp_list):
                for next_itemset in k_fp_list_cp[i+1:]:
                    result, candidate = is_candidate(itemset, next_itemset, k+1)
                    if result:

                        is_duplicated = False
                        for in_candidate in candidate_list:
                            cnt = 0
                            for j in range(k+1):
                                if candidate[j] != in_candidate[j]:
                                    break
                                cnt += 1
                            if cnt == k+1:
                                is_duplicated = True
                                break
                        if not is_duplicated:
                            candidate_list.append(candidate)
            return candidate_list

        def generate_fps(data, candidate_list, min_num):
            fp_list = []
            sup_list = []
            for candidate in candidate_list:
                sup_num = 0
                for itemset in data:
                    if set(itemset).issuperset(set(candidate)):
                        sup_num += 1
                if sup_num >= min_num:
                    fp_list.append(candidate)
                    sup_list.append(sup_num*100/self.total_num)
            if len(sup_list) != 0:
                self.sup_mat.append(sup_list)
            return fp_list

        def is_candidate(itemset, next_itemset, k):
            result = False
            candidate = copy.deepcopy(itemset)
            for item in next_itemset:
                if item not in itemset:
                    candidate.append(item)
            if len(candidate) == k:
                result = True
            return result, sorted(candidate)

        k = 1
        ck = generate_candidates(self.fp[0], k)
        while len(ck) != 0:
            k += 1
            print("C", k, "generated")
            lk = generate_fps(self.data, ck, self.min_support_num)
            print("L", k, "generated")
            if len(lk) == 0:
                break
            self.fp.append(lk)
            ck = generate_candidates(lk, k)

    def get_association_rules(self, row, col):
        fp = set(self.fp[row][col])
        sup = self.sup_mat[row][col]
        ars = []
        for i in range(row):
            for j, sub_fp in enumerate(self.fp[i]):
                sub_fp = set(sub_fp)
                if sub_fp.issubset(fp):
                    ars.append([list(sub_fp), list(fp-sub_fp), sup, sup*100/self.sup_mat[i][j]])
        return ars

    def all_association_rules(self):
        if len(self.fp) > 1:
            for row, fps in enumerate(self.fp):
                if row == 0:
                    continue
                for col in range(len(fps)):
                    ar = self.get_association_rules(row, col)
                    self.ars.append(ar)

    def write_to_output_file(self):
        with open(self.output_file, "w") as f:
            for ars in self.ars:
                for ar in ars:
                    str1 = ', '.join([str(c) for c in ar[0]])
                    str2 = ', '.join([str(c) for c in ar[1]])
                    f.write("{%s}\t{%s}\t%.2f\t%.2f\n"%(str1, str2, ar[2], ar[3]))

if __name__ == "__main__":
    argv = sys.argv[1:]
    min_sup = int(argv[0])
    input_filename = argv[1]
    output_filename = argv[2]

    a = Apriori(min_sup, input_filename, output_filename)
    a.all_frequent_patterns()
    a.all_association_rules()
    a.write_to_output_file()


