#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>

int BATCH_SIZE = -1;
#define MAX_LINE_LENGTH 100
#define FEATURE_COUNT 769
#define WHITE 1
#define BLACK 0
enum {p_P, p_N, p_B, p_R, p_Q, p_K, p_p, p_n, p_b, p_r, p_q, p_k};

int getLineCount(FILE *fp){
    int count = 0;
    char c;
    for (c = getc(fp); c != EOF; c = getc(fp))
        if (c == '\n') // Increment count if this character is newline
            count = count + 1;
    fseek(fp, 0L, SEEK_SET);
    return count;
}

int32_t *features;

char *data;

int32_t pieces[12][64];
int side;

int32_t char_pieces[] = {
        ['P'] = p_P + 1,
        ['N'] = p_N + 1,
        ['B'] = p_B + 1,
        ['R'] = p_R + 1,
        ['Q'] = p_Q + 1,
        ['K'] = p_K + 1,
        ['p'] = p_p + 1,
        ['n'] = p_n + 1,
        ['b'] = p_b + 1,
        ['r'] = p_r + 1,
        ['q'] = p_q + 1,
        ['k'] = p_k + 1
};

void parse_fen(char* fen){
    memset(pieces, 0, sizeof(pieces));

    int square = 0;
    for (int i = 0; i < 100; i++){
        char c = fen[i];
        if (c == ' '){
            assert(fen[i+1] == 'w' || fen[i+1] == 'b');
            if (fen[i+1] == 'w'){
                side = WHITE;
            } else {
                side == BLACK;
            }
            break;
        }
        if (c == '/')
            continue;

        if (char_pieces[c] == 0){
            square += atoi(&fen[i]);
        } else {
            pieces[char_pieces[c]-1][square] = 1;
            square++;
        }
    }
}

char piece_symbols[12] = {
        'P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k'
};

void print_board(){
    int32_t rank = 8;
    for (int32_t square = 0; square < 64; square++){

        if (!(square % 8)) {
            printf("\n");
            printf("%d | ", rank);
            rank--;
        }

        int32_t found_piece = 0;

        for (int32_t piece = p_P; piece <= p_k; piece++){
            if (pieces[piece][square]){
                printf("%c ", piece_symbols[piece]);
                found_piece = 1;
                break;
            }
        }

        if (!found_piece)
            printf(". ");
    }
    printf("\n    _______________\n");
    printf("    A B C D E F G H\n\n");

    printf("side to move : %s", side? "white" : "black");

}

void init(int val, int batchSize){
    BATCH_SIZE = batchSize;
    features = malloc(sizeof(int32_t) * FEATURE_COUNT * BATCH_SIZE);

    FILE *fin = fopen("chessData.csv", "r");

    int count = getLineCount(fin);
    int lineIndex = 0;
    data = malloc(sizeof(char) * count * MAX_LINE_LENGTH);

    char c;
    int cindex = 0;

    for (c = getc(fin); c != EOF; c = getc(fin)){
        data[(lineIndex*100) + cindex] = c;
        cindex++;
        if (c == '\n'){
            data[(lineIndex*100) + cindex - 1] = '\0';
            lineIndex++;
            cindex = 0;
        }

        assert(cindex < MAX_LINE_LENGTH);
    }

    fclose(fin);
}

int *generate_features(int index){
    for (int batch = 0; batch < BATCH_SIZE; batch++) {
        parse_fen(&data[(index * BATCH_SIZE * MAX_LINE_LENGTH) + (batch * MAX_LINE_LENGTH)]);
        memcpy(&features[batch*FEATURE_COUNT], pieces, sizeof(pieces));
        features[batch*FEATURE_COUNT + 768] = side;
    }
    
    return features;
}

#ifdef EXE
int main(){

    init(0, 64);

    generate_features(0);
    

    // parse_fen(data);
    // print_board();

    return 0;
}
#endif
